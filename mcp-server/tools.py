"""
Litera MCP Server — Tools Implementation
Implements MCP tools: search_books, create_order, cancel_order, check_inventory.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from storage import LiteraStorage, OrderCancellationError, InventoryError, StorageError


def get_tool_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "search_books",
            "description": "Поиск книг в каталоге интернет-магазина Litera по названию, автору, ISBN, категории или максимальной стоимости.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос (название произведения, имя автора или ISBN)",
                    },
                    "category": {
                        "type": "string",
                        "description": "Название или slug рубрики (например, 'Программирование и IT', 'it-and-programming', 'fiction')",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Максимальная цена издания в белорусских рублях (BYN)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество возвращаемых результатов (по умолчанию 10)",
                        "default": 10,
                    },
                },
            },
        },
        {
            "name": "check_inventory",
            "description": "Проверка наличия и складских остатков книги по всем филиалам сети и центральному распределительному хабу.",
            "inputSchema": {
                "type": "object",
                "required": ["book_id"],
                "properties": {
                    "book_id": {
                        "type": "string",
                        "description": "UUID идентификатор книги или ISBN (например '978-5-4461-0923-4' или '44444444-4444-4444-4444-444444444401')",
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Опциональный фильтр по UUID филиала или названию точки (например 'ТЦ Галерея')",
                    },
                },
            },
        },
        {
            "name": "create_order",
            "description": "Оформление нового заказа в магазине Litera с валидацией наличия на складе, расчетом доставки и автоматическим резервированием экземпляров.",
            "inputSchema": {
                "type": "object",
                "required": ["user_id", "items", "delivery_type"],
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID или email покупателя (например 'customer@litera.by')",
                    },
                    "items": {
                        "type": "array",
                        "description": "Список позиций для заказа",
                        "items": {
                            "type": "object",
                            "required": ["book_id", "quantity"],
                            "properties": {
                                "book_id": {
                                    "type": "string",
                                    "description": "UUID или ISBN книги",
                                },
                                "quantity": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "description": "Количество экземпляров",
                                },
                            },
                        },
                    },
                    "delivery_type": {
                        "type": "string",
                        "enum": ["COURIER", "PICKUP_BRANCH", "POSTAL_SERVICE"],
                        "description": "Способ получения: COURIER (курьер), PICKUP_BRANCH (самовывоз из магазина), POSTAL_SERVICE (почта)",
                    },
                    "delivery_address": {
                        "type": "string",
                        "description": "Адрес доставки (обязательно при выборе курьерской или почтовой доставки)",
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "UUID филиала для самовывоза (обязательно при PICKUP_BRANCH)",
                    },
                    "contact_phone": {
                        "type": "string",
                        "description": "Контактный номер телефона покупателя",
                    },
                    "contact_name": {
                        "type": "string",
                        "description": "Имя получателя заказа",
                    },
                    "payment_method": {
                        "type": "string",
                        "enum": ["CARD_ONLINE", "SBP", "CASH_ON_DELIVERY", "BONUS_POINTS"],
                        "default": "CARD_ONLINE",
                        "description": "Выбранный метод оплаты",
                    },
                },
            },
        },
        {
            "name": "cancel_order",
            "description": "Отмена заказа с обязательной бизнес-валидацией логистической стадии. Заказы, переданные в доставку (SHIPPED) или врученные покупателю (DELIVERED), отменить через этот метод нельзя.",
            "inputSchema": {
                "type": "object",
                "required": ["order_id", "reason"],
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "UUID или читаемый номер заказа (например 'LIT-20261013-10001')",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Подробная причина отмены заказа покупателем или оператором",
                    },
                },
            },
        },
    ]


def handle_tool_call(storage: LiteraStorage, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes tool and returns standard MCP Tool Result format:
    {"content": [{"type": "text", "text": "..."}], "isError": bool}
    """
    try:
        arguments = arguments or {}
        if tool_name == "search_books":
            results = storage.search_books(
                query=arguments.get("query"),
                category=arguments.get("category"),
                max_price=arguments.get("max_price"),
                limit=arguments.get("limit", 10),
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"found_count": len(results), "books": results}, ensure_ascii=False, indent=2),
                    }
                ],
                "isError": False,
            }

        elif tool_name == "check_inventory":
            book_id = arguments.get("book_id")
            if not book_id:
                raise StorageError("Параметр 'book_id' обязателен для проверки остатков")
            result = storage.check_inventory(book_id=book_id, branch_id=arguments.get("branch_id"))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2),
                    }
                ],
                "isError": False,
            }

        elif tool_name == "create_order":
            order = storage.create_order(
                user_id=arguments.get("user_id", ""),
                items=arguments.get("items", []),
                delivery_type=arguments.get("delivery_type", "COURIER"),
                delivery_address=arguments.get("delivery_address"),
                branch_id=arguments.get("branch_id"),
                contact_phone=arguments.get("contact_phone"),
                contact_name=arguments.get("contact_name"),
                payment_method=arguments.get("payment_method", "CARD_ONLINE"),
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "status": "SUCCESS",
                                "message": f"Заказ {order['order_number']} успешно создан и зарезервирован на складе.",
                                "order": order,
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
                    }
                ],
                "isError": False,
            }

        elif tool_name == "cancel_order":
            order_id = arguments.get("order_id", "")
            reason = arguments.get("reason", "")
            cancellation = storage.cancel_order(order_id=order_id, reason=reason)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(cancellation, ensure_ascii=False, indent=2),
                    }
                ],
                "isError": False,
            }

        else:
            return {
                "content": [{"type": "text", "text": f"Неизвестный инструмент: '{tool_name}'"}],
                "isError": True,
            }

    except OrderCancellationError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "error_type": "ORDER_CANCELLATION_CONFLICT",
                        "error_message": str(e),
                        "recommendation": "Используйте prompt 'refund_calculation' для расчета частичного возврата по регламенту возвратов."
                    }, ensure_ascii=False, indent=2)
                }
            ],
            "isError": True,
        }
    except InventoryError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "error_type": "INSUFFICIENT_STOCK",
                        "error_message": str(e),
                    }, ensure_ascii=False, indent=2)
                }
            ],
            "isError": True,
        }
    except StorageError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "error_type": "VALIDATION_OR_STORAGE_ERROR",
                        "error_message": str(e),
                    }, ensure_ascii=False, indent=2)
                }
            ],
            "isError": True,
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Внутренняя ошибка при выполнении инструмента {tool_name}: {str(e)}",
                }
            ],
            "isError": True,
        }
