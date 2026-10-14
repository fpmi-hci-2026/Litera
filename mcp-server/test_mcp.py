"""
Comprehensive Test Suite for Litera MCP Server
Uses Python's standard unittest library.
Tests storage, tools, resources, prompts, business rules, and JSON-RPC protocol.
"""

from __future__ import annotations

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompts import get_prompt_definitions, render_prompt
from resources import get_resource_definitions, read_resource
from server import McpServer
from storage import InventoryError, LiteraStorage, OrderCancellationError, StorageError
from tools import get_tool_definitions, handle_tool_call


class TestLiteraStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = LiteraStorage(":memory:")

    def test_search_books_by_title(self) -> None:
        results = self.storage.search_books(query="Чистый код")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Чистый код: создание, анализ и рефакторинг")
        self.assertEqual(results[0]["author"], "Роберт Мартин")

    def test_search_books_case_insensitive_cyrillic(self) -> None:
        # Lowercase Cyrillic search query must match title, author, and description
        results_lower = self.storage.search_books(query="чистый")
        self.assertGreaterEqual(len(results_lower), 1)
        self.assertEqual(results_lower[0]["title"], "Чистый код: создание, анализ и рефакторинг")

        results_author = self.storage.search_books(query="роберт мартин")
        self.assertGreaterEqual(len(results_author), 1)

        results_desc = self.storage.search_books(query="антиутопия")
        self.assertGreaterEqual(len(results_desc), 1)

    def test_search_books_by_category(self) -> None:
        results = self.storage.search_books(category="it-and-programming")
        self.assertGreaterEqual(len(results), 2)
        for b in results:
            self.assertEqual(b["category_name"], "Программирование и IT")

    def test_search_books_by_max_price(self) -> None:
        results = self.storage.search_books(max_price=30.0)
        self.assertTrue(len(results) > 0)
        for b in results:
            price = b["discount_price"] if b["discount_price"] is not None else b["price"]
            self.assertLessEqual(price, 30.0)

    def test_check_inventory_success(self) -> None:
        inv = self.storage.check_inventory("44444444-4444-4444-4444-444444444401")
        self.assertEqual(inv["title"], "Чистый код: создание, анализ и рефакторинг")
        self.assertGreater(inv["total_available"], 0)
        self.assertGreaterEqual(len(inv["branches"]), 2)

    def test_check_inventory_isbn_without_hyphens(self) -> None:
        # ISBN 978-5-4461-0923-4 queried as 9785446109234
        inv = self.storage.check_inventory("9785446109234")
        self.assertEqual(inv["title"], "Чистый код: создание, анализ и рефакторинг")
        self.assertGreater(inv["total_available"], 0)

    def test_check_inventory_not_found(self) -> None:
        with self.assertRaises(StorageError):
            self.storage.check_inventory("00000000-0000-0000-0000-000000000000")

    def test_create_order_courier_success(self) -> None:
        order = self.storage.create_order(
            user_id="customer@litera.by",
            items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 1}],
            delivery_type="COURIER",
            delivery_address="г. Минск, ул. Козлова, 15",
            contact_name="Анна Савицкая",
            contact_phone="+375291112233",
        )
        self.assertTrue(order["order_number"].startswith("LIT-"))
        self.assertEqual(order["status"], "PENDING_PAYMENT")
        self.assertEqual(order["delivery_cost"], 5.0)
        self.assertEqual(len(order["items"]), 1)

    def test_create_order_insufficient_stock(self) -> None:
        with self.assertRaises(InventoryError):
            self.storage.create_order(
                user_id="customer@litera.by",
                items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 9999}],
                delivery_type="COURIER",
                delivery_address="г. Минск",
            )

    def test_create_order_missing_address_validation(self) -> None:
        with self.assertRaises(StorageError):
            self.storage.create_order(
                user_id="customer@litera.by",
                items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 1}],
                delivery_type="COURIER",
                delivery_address="",  # Empty address for courier
            )

    def test_create_order_missing_branch_validation(self) -> None:
        with self.assertRaises(StorageError):
            self.storage.create_order(
                user_id="customer@litera.by",
                items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 1}],
                delivery_type="PICKUP_BRANCH",
                branch_id=None,  # Missing branch for pickup
            )

    def test_create_order_postal_service_validation(self) -> None:
        with self.assertRaises(StorageError):
            self.storage.create_order(
                user_id="customer@litera.by",
                items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 1}],
                delivery_type="POSTAL_SERVICE",
                delivery_address="",  # Empty address for postal delivery
            )
        # Success when address provided
        order = self.storage.create_order(
            user_id="customer@litera.by",
            items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 1}],
            delivery_type="POSTAL_SERVICE",
            delivery_address="г. Брест, ул. Ленина, 10, кв. 5",
        )
        self.assertEqual(order["delivery_type"], "POSTAL_SERVICE")
        self.assertEqual(order["delivery_cost"], 4.0)

    def test_cancel_order_allowed_status(self) -> None:
        # Initial order LIT-20261013-10001 is in PROCESSING
        result = self.storage.cancel_order("LIT-20261013-10001", "Клиент изменил решение")
        self.assertEqual(result["status"], "CANCELLED")
        self.assertEqual(result["previous_status"], "PROCESSING")
        self.assertIn("успешно отменен", result["message"])

    def test_cancel_order_releases_stock_only_for_target_branch(self) -> None:
        # Create an order specifically for branch 2
        order = self.storage.create_order(
            user_id="customer@litera.by",
            items=[{"book_id": "44444444-4444-4444-4444-444444444401", "quantity": 1}],
            delivery_type="PICKUP_BRANCH",
            branch_id="33333333-3333-3333-3333-333333333302",
        )
        # Check reserved before cancellation
        c = self.storage.conn.cursor()
        c.execute("SELECT reserved FROM stock_items WHERE book_id = '44444444-4444-4444-4444-444444444401' AND branch_id = '33333333-3333-3333-3333-333333333301'")
        reserved_b1_before = c.fetchone()[0]

        c.execute("SELECT reserved FROM stock_items WHERE book_id = '44444444-4444-4444-4444-444444444401' AND branch_id = '33333333-3333-3333-3333-333333333302'")
        reserved_b2_before = c.fetchone()[0]

        # Cancel order
        self.storage.cancel_order(order["order_id"], "Отмена самовывоза")

        c.execute("SELECT reserved FROM stock_items WHERE book_id = '44444444-4444-4444-4444-444444444401' AND branch_id = '33333333-3333-3333-3333-333333333301'")
        reserved_b1_after = c.fetchone()[0]

        c.execute("SELECT reserved FROM stock_items WHERE book_id = '44444444-4444-4444-4444-444444444401' AND branch_id = '33333333-3333-3333-3333-333333333302'")
        reserved_b2_after = c.fetchone()[0]

        # Branch 1 should NOT be touched!
        self.assertEqual(reserved_b1_before, reserved_b1_after)
        # Branch 2 should have decreased by 1
        self.assertEqual(reserved_b2_after, reserved_b2_before - 1)

    def test_cancel_order_forbidden_when_delivered(self) -> None:
        # Initial order LIT-20261012-10002 is DELIVERED
        with self.assertRaises(OrderCancellationError) as ctx:
            self.storage.cancel_order("LIT-20261012-10002", "Хочу отменить")
        self.assertIn("DELIVERED", str(ctx.exception))

    def test_calculate_refund_for_shipped_order(self) -> None:
        calc = self.storage.calculate_refund("LIT-20261012-10002", "Возврат брака")
        self.assertEqual(calc["order_number"], "LIT-20261012-10002")
        self.assertGreater(calc["refundable_amount"], 0)


class TestMcpTools(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = LiteraStorage(":memory:")

    def test_tool_definitions_list(self) -> None:
        tools = get_tool_definitions()
        names = [t["name"] for t in tools]
        self.assertIn("search_books", names)
        self.assertIn("check_inventory", names)
        self.assertIn("create_order", names)
        self.assertIn("cancel_order", names)

    def test_tool_search_books_call(self) -> None:
        res = handle_tool_call(self.storage, "search_books", {"query": "Оруэлл"})
        self.assertFalse(res["isError"])
        data = json.loads(res["content"][0]["text"])
        self.assertGreaterEqual(data["found_count"], 1)
        self.assertIn("1984", data["books"][0]["title"])

    def test_tool_check_inventory_call(self) -> None:
        res = handle_tool_call(self.storage, "check_inventory", {"book_id": "978-5-17-080115-2"})
        self.assertFalse(res["isError"])
        data = json.loads(res["content"][0]["text"])
        self.assertEqual(data["title"], "1984")
        self.assertGreater(data["total_available"], 0)

    def test_tool_create_order_call(self) -> None:
        res = handle_tool_call(
            self.storage,
            "create_order",
            {
                "user_id": "customer@litera.by",
                "items": [{"book_id": "978-5-17-080115-2", "quantity": 1}],
                "delivery_type": "COURIER",
                "delivery_address": "Минск, пр. Независимости, 4",
            },
        )
        self.assertFalse(res["isError"])
        data = json.loads(res["content"][0]["text"])
        self.assertEqual(data["status"], "SUCCESS")

    def test_tool_cancel_order_delivered_validation_error(self) -> None:
        # Order 2 is DELIVERED
        res = handle_tool_call(
            self.storage,
            "cancel_order",
            {"order_id": "LIT-20261012-10002", "reason": "Передумал"},
        )
        self.assertTrue(res["isError"])
        data = json.loads(res["content"][0]["text"])
        self.assertEqual(data["error_type"], "ORDER_CANCELLATION_CONFLICT")


class TestMcpResourcesAndPrompts(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = LiteraStorage(":memory:")

    def test_resource_definitions(self) -> None:
        defs = get_resource_definitions()
        uris = [r["uri"] for r in defs["resources"]]
        self.assertIn("books://catalog", uris)
        self.assertIn("orders://recent", uris)
        templates = [t["uriTemplate"] for t in defs["resourceTemplates"]]
        self.assertIn("orders://user/{id}/history", templates)

    def test_read_books_catalog(self) -> None:
        res = read_resource(self.storage, "books://catalog")
        self.assertEqual(res["contents"][0]["uri"], "books://catalog")
        data = json.loads(res["contents"][0]["text"])
        self.assertGreaterEqual(data["total_titles"], 5)

    def test_read_recent_orders(self) -> None:
        res = read_resource(self.storage, "orders://recent")
        self.assertEqual(res["contents"][0]["uri"], "orders://recent")
        data = json.loads(res["contents"][0]["text"])
        self.assertGreaterEqual(data["count"], 2)

    def test_read_user_order_history(self) -> None:
        res = read_resource(self.storage, "orders://user/customer@litera.by/history")
        data = json.loads(res["contents"][0]["text"])
        self.assertEqual(data["user_id"], "customer@litera.by")
        self.assertGreaterEqual(data["orders_count"], 2)

    def test_read_user_order_history_percent_encoded_email(self) -> None:
        # Standard MCP clients may percent-encode '@' as '%40' in URI
        res = read_resource(self.storage, "orders://user/customer%40litera.by/history")
        data = json.loads(res["contents"][0]["text"])
        self.assertEqual(data["user_id"], "customer@litera.by")
        self.assertGreaterEqual(data["orders_count"], 2)

    def test_render_order_assistance_prompt(self) -> None:
        prompts = get_prompt_definitions()
        names = [p["name"] for p in prompts]
        self.assertIn("order_assistance", names)
        rendered = render_prompt(
            self.storage,
            "order_assistance",
            {"preferences": "книги по чистой архитектуре", "budget": "100"},
        )
        self.assertIn("консультант книжного онлайн-магазина «Litera»", rendered["messages"][0]["content"]["text"])

    def test_render_order_assistance_prompt_with_budget_filtering(self) -> None:
        # Budget 30 BYN should filter out expensive 60-80 BYN books
        rendered = render_prompt(
            self.storage,
            "order_assistance",
            {"preferences": "роман", "budget": "30"},
        )
        self.assertIn("30", rendered["messages"][0]["content"]["text"])
        # Book 1984 costs 24.50 and should be included
        self.assertIn("1984", rendered["messages"][0]["content"]["text"])

    def test_handle_tool_call_none_arguments(self) -> None:
        res = handle_tool_call(self.storage, "search_books", None)
        self.assertFalse(res["isError"])

    def test_render_refund_calculation_prompt(self) -> None:
        rendered = render_prompt(
            self.storage,
            "refund_calculation",
            {"order_id": "LIT-20261012-10002", "reason": "Брак обложки"},
        )
        self.assertIn("возврата", rendered["messages"][0]["content"]["text"])


class TestMcpJsonRpcServer(unittest.TestCase):
    def setUp(self) -> None:
        self.server = McpServer(":memory:")

    def test_initialize_handshake(self) -> None:
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        }
        res = self.server.handle_request(req)
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["serverInfo"]["name"], "litera-bookstore-mcp-server")
        self.assertIn("tools", res["result"]["capabilities"])

        # Send notification
        notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        res2 = self.server.handle_request(notify)
        self.assertIsNone(res2)
        self.assertTrue(self.server.initialized)

    def test_tools_list_rpc(self) -> None:
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        res = self.server.handle_request(req)
        tools = res["result"]["tools"]
        self.assertEqual(len(tools), 4)

    def test_tools_call_rpc(self) -> None:
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "search_books", "arguments": {"query": "Булгаков"}},
        }
        res = self.server.handle_request(req)
        self.assertEqual(res["id"], 3)
        self.assertFalse(res["result"]["isError"])
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(data["books"][0]["author"], "Михаил Булгаков")

    def test_resources_list_rpc(self) -> None:
        req = {"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}}
        res = self.server.handle_request(req)
        self.assertIn("resources", res["result"])
        self.assertIn("resourceTemplates", res["result"])

    def test_resources_read_rpc(self) -> None:
        req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/read",
            "params": {"uri": "books://catalog"},
        }
        res = self.server.handle_request(req)
        self.assertEqual(res["result"]["contents"][0]["uri"], "books://catalog")

    def test_prompts_list_and_get_rpc(self) -> None:
        req_list = {"jsonrpc": "2.0", "id": 6, "method": "prompts/list", "params": {}}
        res_list = self.server.handle_request(req_list)
        self.assertEqual(len(res_list["result"]["prompts"]), 2)

        req_get = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "prompts/get",
            "params": {"name": "refund_calculation", "arguments": {"order_id": "LIT-20261013-10001", "reason": "Отказ"}},
        }
        res_get = self.server.handle_request(req_get)
        self.assertIn("messages", res_get["result"])

    def test_method_not_found_rpc(self) -> None:
        req = {"jsonrpc": "2.0", "id": 8, "method": "unknown_method", "params": {}}
        res = self.server.handle_request(req)
        self.assertEqual(res["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
