"""
Litera MCP Server — SQLite Storage & Mock Repository
Provides in-memory or file-backed SQLite database initialized with domain data
matching the Litera PostgreSQL schema.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


class StorageError(Exception):
    """Custom storage exception."""
    pass


class OrderCancellationError(StorageError):
    """Raised when an order cannot be cancelled due to lifecycle stage."""
    pass


class InventoryError(StorageError):
    """Raised when an inventory operation violates stock limits."""
    pass


class LiteraStorage:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.create_function("lower", 1, lambda s: s.lower() if s is not None else "")
        self._init_schema()
        self._seed_data()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS books (
                id TEXT PRIMARY KEY,
                isbn TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category_id TEXT,
                price REAL NOT NULL,
                discount_price REAL,
                cover_url TEXT,
                preview_pdf_url TEXT,
                description TEXT,
                publication_year INTEGER,
                pages INTEGER,
                format TEXT DEFAULT 'HARDCOVER',
                rating REAL DEFAULT 5.0,
                reviews_count INTEGER DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS branches (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT DEFAULT 'Минск',
                phone TEXT,
                work_hours TEXT,
                is_warehouse INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS stock_items (
                id TEXT PRIMARY KEY,
                book_id TEXT NOT NULL,
                branch_id TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                reserved INTEGER NOT NULL DEFAULT 0,
                shelf_location TEXT,
                UNIQUE(book_id, branch_id),
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (branch_id) REFERENCES branches(id)
            );

            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                role TEXT DEFAULT 'CUSTOMER',
                bonus_balance INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                order_number TEXT UNIQUE NOT NULL,
                user_id TEXT,
                branch_id TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING_PAYMENT',
                payment_method TEXT DEFAULT 'CARD_ONLINE',
                payment_status TEXT DEFAULT 'PENDING',
                items_total REAL NOT NULL,
                delivery_cost REAL DEFAULT 0.0,
                total_price REAL NOT NULL,
                delivery_type TEXT NOT NULL,
                delivery_address TEXT,
                contact_phone TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                cancel_reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (branch_id) REFERENCES branches(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                book_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            );
            """)

    def _seed_data(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] > 0:
            return

        with self.conn:
            # Categories
            categories = [
                ("11111111-1111-1111-1111-111111111101", "Программирование и IT", "it-and-programming", "Архитектура, языки, паттерны"),
                ("11111111-1111-1111-1111-111111111102", "Художественная литература", "fiction", "Мировая классика"),
                ("11111111-1111-1111-1111-111111111103", "Научная фантастика", "science-fiction", "Космос, антиутопии"),
                ("11111111-1111-1111-1111-111111111104", "Психология и продуктивность", "psychology", "Саморазвитие"),
            ]
            self.conn.executemany("INSERT INTO categories VALUES (?, ?, ?, ?)", categories)

            # Users
            users = [
                ("22222222-2222-2222-2222-222222222201", "admin@litera.by", "Кирилл Зайдаль (Администратор)", "+375291234567", "ADMIN", 1000),
                ("22222222-2222-2222-2222-222222222202", "warehouse@litera.by", "Алексей Смирнов (Склад)", "+375297654321", "WAREHOUSE_MANAGER", 200),
                ("22222222-2222-2222-2222-222222222203", "customer@litera.by", "Анна-Мария Савицкая (Покупатель)", "+375449876543", "CUSTOMER", 350),
            ]
            self.conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", users)

            # Branches
            branches = [
                ("33333333-3333-3333-3333-333333333301", "Центральный хаб «Платонова»", "ул. Платонова, 39", "Минск", "+375172001122", "08:00 - 20:00", 1),
                ("33333333-3333-3333-3333-333333333302", "Филиал «ТЦ Галерея»", "пр-т Победителей, 9", "Минск", "+375173002233", "10:00 - 22:00", 0),
                ("33333333-3333-3333-3333-333333333303", "Филиал «ТЦ Dana Mall»", "ул. Петра Мстиславца, 11", "Минск", "+375174003344", "10:00 - 22:00", 0),
            ]
            self.conn.executemany("INSERT INTO branches VALUES (?, ?, ?, ?, ?, ?, ?)", branches)

            # Books
            books = [
                ("44444444-4444-4444-4444-444444444401", "978-5-4461-0923-4", "Чистый код: создание, анализ и рефакторинг", "Роберт Мартин", "11111111-1111-1111-1111-111111111101", 65.50, 58.90, "https://cdn.litera.by/covers/clean-code.jpg", "https://cdn.litera.by/previews/clean-code-preview.pdf", "Руководство по написанию чистого и читаемого программного кода.", 2023, 464, "HARDCOVER", 4.90, 42),
                ("44444444-4444-4444-4444-444444444402", "978-5-4461-1287-6", "Паттерны микросервисной архитектуры", "Крис Ричардсон", "11111111-1111-1111-1111-111111111101", 82.00, None, "https://cdn.litera.by/covers/microservices-patterns.jpg", "https://cdn.litera.by/previews/microservices-preview.pdf", "Паттерны декомпозиции монолитов, саги и распределенные транзакции.", 2022, 544, "HARDCOVER", 4.85, 28),
                ("44444444-4444-4444-4444-444444444403", "978-5-17-090835-6", "Мастер и Маргарита", "Михаил Булгаков", "11111111-1111-1111-1111-111111111102", 32.40, 29.00, "https://cdn.litera.by/covers/master-margarita.jpg", "https://cdn.litera.by/previews/master-margarita-preview.pdf", "Культовый роман русской классики.", 2021, 512, "HARDCOVER", 4.95, 115),
                ("44444444-4444-4444-4444-444444444404", "978-5-17-080115-2", "1984", "Джордж Оруэлл", "11111111-1111-1111-1111-111111111103", 24.50, None, "https://cdn.litera.by/covers/1984.jpg", "https://cdn.litera.by/previews/1984-preview.pdf", "Роман-антиутопия о тоталитарном режиме.", 2022, 320, "PAPERBACK", 4.90, 89),
                ("44444444-4444-4444-4444-444444444405", "978-5-04-099344-4", "Атомные привычки", "Джеймс Клир", "11111111-1111-1111-1111-111111111104", 38.00, 34.20, "https://cdn.litera.by/covers/atomic-habits.jpg", "https://cdn.litera.by/previews/atomic-habits-preview.pdf", "Простая методика формирования полезных привычек.", 2023, 304, "HARDCOVER", 4.80, 76),
            ]
            self.conn.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", books)

            # Stock Items
            stock_items = [
                ("55555555-5555-5555-5555-555555555501", "44444444-4444-4444-4444-444444444401", "33333333-3333-3333-3333-333333333301", 35, 2, "A-12-04"),
                ("55555555-5555-5555-5555-555555555502", "44444444-4444-4444-4444-444444444401", "33333333-3333-3333-3333-333333333302", 5, 0, "S-02-11"),
                ("55555555-5555-5555-5555-555555555503", "44444444-4444-4444-4444-444444444402", "33333333-3333-3333-3333-333333333301", 20, 1, "A-14-02"),
                ("55555555-5555-5555-5555-555555555504", "44444444-4444-4444-4444-444444444403", "33333333-3333-3333-3333-333333333302", 12, 1, "B-01-05"),
                ("55555555-5555-5555-5555-555555555505", "44444444-4444-4444-4444-444444444404", "33333333-3333-3333-3333-333333333303", 18, 0, "C-05-09"),
                ("55555555-5555-5555-5555-555555555506", "44444444-4444-4444-4444-444444444405", "33333333-3333-3333-3333-333333333301", 40, 3, "D-08-01"),
            ]
            self.conn.executemany("INSERT INTO stock_items VALUES (?, ?, ?, ?, ?, ?)", stock_items)

            # Orders
            orders = [
                ("66666666-6666-6666-6666-666666666601", "LIT-20261013-10001", "22222222-2222-2222-2222-222222222203", "33333333-3333-3333-3333-333333333302", "PROCESSING", "CARD_ONLINE", "CAPTURED", 58.90, 0.00, 58.90, "PICKUP_BRANCH", "Самовывоз из ТЦ Галерея", "+375449876543", "Анна-Мария Савицкая", None, "2026-10-13T10:15:00Z"),
                ("66666666-6666-6666-6666-666666666602", "LIT-20261012-10002", "22222222-2222-2222-2222-222222222203", None, "DELIVERED", "SBP", "CAPTURED", 114.40, 5.00, 119.40, "COURIER", "г. Минск, пр-т Независимости, 4, кв. 12", "+375449876543", "Анна-Мария Савицкая", None, "2026-10-12T14:20:00Z"),
            ]
            self.conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", orders)

            # Order items
            order_items = [
                ("77777777-7777-7777-7777-777777777701", "66666666-6666-6666-6666-666666666601", "44444444-4444-4444-4444-444444444401", 1, 58.90, 58.90),
                ("77777777-7777-7777-7777-777777777702", "66666666-6666-6666-6666-666666666602", "44444444-4444-4444-4444-444444444402", 1, 82.00, 82.00),
                ("77777777-7777-7777-7777-777777777703", "66666666-6666-6666-6666-666666666602", "44444444-4444-4444-4444-444444444403", 1, 32.40, 32.40),
            ]
            self.conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)", order_items)

    # =========================================================================
    # Storage Queries and Mutations
    # =========================================================================

    def search_books(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        sql = """
        SELECT b.id, b.isbn, b.title, b.author, b.price, b.discount_price,
               b.format, b.rating, b.reviews_count, b.cover_url, b.preview_pdf_url,
               b.description, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE 1=1
        """
        params: List[Any] = []

        if query:
            q_clean = query.strip().lower()
            q_like = f"%{q_clean}%"
            sql += " AND (lower(b.title) LIKE ? OR lower(b.author) LIKE ? OR lower(b.isbn) LIKE ? OR lower(b.description) LIKE ?)"
            params.extend([q_like, q_like, q_like, q_like])

        if category:
            cat_clean = category.strip().lower()
            cat_like = f"%{cat_clean}%"
            sql += " AND (lower(c.name) LIKE ? OR lower(c.slug) LIKE ?)"
            params.extend([cat_like, cat_like])

        if max_price is not None:
            sql += " AND (COALESCE(b.discount_price, b.price) <= ?)"
            params.append(max_price)

        sql += " ORDER BY b.rating DESC LIMIT ?"
        params.append(max(1, min(limit, 50)))

        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def check_inventory(
        self,
        book_id: str,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        clean_id = book_id.strip()
        cursor.execute("""
        SELECT id, title, author, price FROM books
        WHERE id = ? OR isbn = ? OR REPLACE(isbn, '-', '') = REPLACE(?, '-', '')
        """, (clean_id, clean_id, clean_id))
        book = cursor.fetchone()
        if not book:
            raise StorageError(f"Книга с ID/ISBN '{book_id}' не найдена в каталоге")

        actual_book_id = book["id"]
        sql = """
        SELECT s.id, s.branch_id, br.name as branch_name, br.address,
               s.quantity, s.reserved, (s.quantity - s.reserved) as available,
               s.shelf_location, br.is_warehouse
        FROM stock_items s
        JOIN branches br ON s.branch_id = br.id
        WHERE s.book_id = ?
        """
        params: List[Any] = [actual_book_id]
        if branch_id:
            sql += " AND (s.branch_id = ? OR br.name LIKE ?)"
            params.extend([branch_id, f"%{branch_id}%"])

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        stock_list = [dict(r) for r in rows]
        total_available = sum(max(0, item["available"]) for item in stock_list)

        return {
            "book_id": actual_book_id,
            "title": book["title"],
            "author": book["author"],
            "total_available": total_available,
            "branches": stock_list,
        }

    def create_order(
        self,
        user_id: str,
        items: List[Dict[str, Any]],
        delivery_type: str,
        delivery_address: Optional[str] = None,
        branch_id: Optional[str] = None,
        contact_phone: Optional[str] = None,
        contact_name: Optional[str] = None,
        payment_method: str = "CARD_ONLINE",
    ) -> Dict[str, Any]:
        if not items:
            raise StorageError("Заказ не может быть пустым — укажите хотя бы одну книгу")

        # Normalize delivery type
        dtype = delivery_type.upper().strip()
        if dtype not in ("COURIER", "PICKUP_BRANCH", "POSTAL_SERVICE"):
            raise StorageError(f"Недопустимый тип доставки '{delivery_type}'. Разрешены: COURIER, PICKUP_BRANCH, POSTAL_SERVICE")

        if dtype == "PICKUP_BRANCH" and not branch_id:
            raise StorageError("Для самовывоза необходимо указать идентификатор филиала (branch_id)")
        if dtype in ("COURIER", "POSTAL_SERVICE") and not delivery_address:
            raise StorageError(f"Для доставки ({dtype}) необходимо указать точный адрес (delivery_address)")

        cursor = self.conn.cursor()
        # Find or use user
        cursor.execute("SELECT id, full_name, phone FROM users WHERE id = ? OR email = ?", (user_id, user_id))
        user_row = cursor.fetchone()
        actual_user_id = user_row["id"] if user_row else None
        c_name = contact_name or (user_row["full_name"] if user_row else "Покупатель")
        c_phone = contact_phone or (user_row["phone"] if user_row else "+375000000000")

        # Validate books and compute totals
        order_items_data: List[Dict[str, Any]] = []
        items_total = 0.0
        assigned_branch_id = branch_id

        with self.conn:
            for it in items:
                b_id = str(it.get("book_id", "")).strip()
                qty = int(it.get("quantity", 1))
                if qty <= 0:
                    raise StorageError(f"Некорректное количество {qty} для товара {b_id}")

                cursor.execute("""
                SELECT id, title, price, discount_price FROM books
                WHERE id = ? OR isbn = ? OR REPLACE(isbn, '-', '') = REPLACE(?, '-', '')
                """, (b_id, b_id, b_id))
                bk = cursor.fetchone()
                if not bk:
                    raise StorageError(f"Книга с ID/ISBN '{b_id}' не найдена")

                actual_b_id = bk["id"]
                unit_price = float(bk["discount_price"]) if bk["discount_price"] else float(bk["price"])
                line_total = round(unit_price * qty, 2)
                items_total += line_total

                # Check and reserve stock
                if branch_id:
                    cursor.execute("""
                    SELECT id, branch_id, quantity, reserved FROM stock_items
                    WHERE book_id = ? AND branch_id = ?
                    """, (actual_b_id, branch_id))
                else:
                    cursor.execute("""
                    SELECT id, branch_id, quantity, reserved FROM stock_items
                    WHERE book_id = ?
                    ORDER BY (quantity - reserved) DESC LIMIT 1
                    """, (actual_b_id,))

                stk = cursor.fetchone()
                if not stk or (stk["quantity"] - stk["reserved"]) < qty:
                    available = (stk["quantity"] - stk["reserved"]) if stk else 0
                    raise InventoryError(
                        f"Недостаточно остатков книги '{bk['title']}' (запрошено: {qty}, доступно: {available})"
                    )

                if not assigned_branch_id:
                    assigned_branch_id = stk["branch_id"]

                # Reserve items
                cursor.execute("""
                UPDATE stock_items SET reserved = reserved + ? WHERE id = ?
                """, (qty, stk["id"]))

                order_items_data.append({
                    "id": str(uuid.uuid4()),
                    "book_id": actual_b_id,
                    "title": bk["title"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_price": line_total,
                })

            delivery_cost = 5.0 if dtype == "COURIER" else (4.0 if dtype == "POSTAL_SERVICE" else 0.0)
            total_price = round(items_total + delivery_cost, 2)
            order_id = str(uuid.uuid4())
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
            rand_seq = str(uuid.uuid4().int % 100000).zfill(5)
            order_number = f"LIT-{date_part}-{rand_seq}"

            cursor.execute("""
            INSERT INTO orders (
                id, order_number, user_id, branch_id, status, payment_method,
                payment_status, items_total, delivery_cost, total_price,
                delivery_type, delivery_address, contact_phone, contact_name,
                cancel_reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id, order_number, actual_user_id, assigned_branch_id, "PENDING_PAYMENT",
                payment_method, "PENDING", items_total, delivery_cost, total_price,
                dtype, delivery_address, c_phone, c_name, None, now_iso
            ))

            for oi in order_items_data:
                cursor.execute("""
                INSERT INTO order_items (id, order_id, book_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (oi["id"], order_id, oi["book_id"], oi["quantity"], oi["unit_price"], oi["total_price"]))

        return {
            "order_id": order_id,
            "order_number": order_number,
            "status": "PENDING_PAYMENT",
            "items_total": items_total,
            "delivery_cost": delivery_cost,
            "total_price": total_price,
            "delivery_type": dtype,
            "delivery_address": delivery_address,
            "items": order_items_data,
            "created_at": now_iso,
        }

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        """
        Cancels an order with strict delivery state validation.
        Orders that are SHIPPED, DELIVERED, or already CANCELLED cannot be cancelled.
        """
        if not reason or len(reason.strip()) < 3:
            raise StorageError("Необходимо указать подробную причину отмены заказа")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ? OR order_number = ?", (order_id, order_id))
        order = cursor.fetchone()
        if not order:
            raise StorageError(f"Заказ '{order_id}' не найден")

        current_status = order["status"]
        # Non-cancellable statuses
        if current_status in ("SHIPPED", "DELIVERED"):
            raise OrderCancellationError(
                f"Невозможно отменить заказ в статусе '{current_status}'. "
                f"Заказ уже передан в доставку или вручен клиенту. "
                f"Для возврата используйте регламент возврата товара (refund_calculation)."
            )
        if current_status in ("CANCELLED", "REFUNDED"):
            raise OrderCancellationError(f"Заказ уже находится в финальном статусе '{current_status}'")

        with self.conn:
            # Release reserved items
            cursor.execute("SELECT book_id, quantity FROM order_items WHERE order_id = ?", (order["id"],))
            items = cursor.fetchall()
            order_branch = order["branch_id"]
            for it in items:
                if order_branch:
                    cursor.execute("""
                    UPDATE stock_items
                    SET reserved = MAX(0, reserved - ?)
                    WHERE book_id = ? AND branch_id = ?
                    """, (it["quantity"], it["book_id"], order_branch))
                else:
                    cursor.execute("""
                    UPDATE stock_items
                    SET reserved = MAX(0, reserved - ?)
                    WHERE id = (
                        SELECT id FROM stock_items
                        WHERE book_id = ? AND reserved > 0
                        ORDER BY reserved DESC LIMIT 1
                    )
                    """, (it["quantity"], it["book_id"]))

            cursor.execute("""
            UPDATE orders
            SET status = 'CANCELLED', cancel_reason = ?
            WHERE id = ?
            """, (reason.strip(), order["id"]))

        return {
            "order_id": order["id"],
            "order_number": order["order_number"],
            "previous_status": current_status,
            "status": "CANCELLED",
            "cancel_reason": reason.strip(),
            "released_items_count": len(items),
            "message": "Заказ успешно отменен, зарезервированные остатки на складе возвращены.",
        }

    def get_catalog(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT b.id, b.isbn, b.title, b.author, b.price, b.discount_price,
               b.format, b.rating, b.reviews_count, c.name as category,
               COALESCE(SUM(s.quantity - s.reserved), 0) as in_stock_total
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN stock_items s ON b.id = s.book_id
        GROUP BY b.id
        ORDER BY b.rating DESC
        """)
        return [dict(r) for r in cursor.fetchall()]

    def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT o.id, o.order_number, o.status, o.total_price, o.delivery_type,
               o.created_at, u.full_name as customer_name, u.email
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

    def get_user_order_history(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ? OR email = ?", (user_id, user_id))
        user_row = cursor.fetchone()
        actual_id = user_row["id"] if user_row else user_id

        cursor.execute("""
        SELECT o.id, o.order_number, o.status, o.total_price, o.payment_method,
               o.delivery_type, o.created_at, o.cancel_reason
        FROM orders o
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
        """, (actual_id,))
        orders = [dict(r) for r in cursor.fetchall()]

        for o in orders:
            cursor.execute("""
            SELECT oi.quantity, oi.unit_price, oi.total_price, b.title, b.author, b.isbn
            FROM order_items oi
            JOIN books b ON oi.book_id = b.id
            WHERE oi.order_id = ?
            """, (o["id"],))
            o["items"] = [dict(r) for r in cursor.fetchall()]

        return orders

    def calculate_refund(self, order_id: str, reason: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ? OR order_number = ?", (order_id, order_id))
        order = cursor.fetchone()
        if not order:
            raise StorageError(f"Заказ '{order_id}' не найден")

        status = order["status"]
        total = float(order["total_price"])
        delivery_cost = float(order["delivery_cost"])
        items_total = float(order["items_total"])

        # Business rules for refund calculation
        if status in ("PENDING_PAYMENT",):
            refundable_amount = 0.0
            explanation = "Заказ еще не был оплачен. Списание средств не производилось, возврат не требуется."
        elif status in ("PAID", "PROCESSING", "PACKED"):
            refundable_amount = total
            explanation = "Полный возврат: заказ отменен до передачи в логистическую службу. Возвращается 100% стоимости (включая доставку)."
        elif status == "SHIPPED":
            refundable_amount = items_total
            explanation = "Частичный возврат: заказ уже передан курьеру/службе доставки. Стоимость книг возвращается в полном объеме, стоимость доставки удерживается."
        elif status == "DELIVERED":
            refundable_amount = items_total
            explanation = "Возврат после вручения: возврат товара надлежащего качества возможен в течение 14 дней. Стоимость доставки не возмещается."
        elif status == "CANCELLED":
            refundable_amount = 0.0
            explanation = "Заказ уже отменен ранее."
        else:
            refundable_amount = 0.0
            explanation = f"Неизвестный статус {status}."

        return {
            "order_number": order["order_number"],
            "current_status": status,
            "total_paid": total,
            "items_cost": items_total,
            "delivery_cost": delivery_cost,
            "refundable_amount": round(refundable_amount, 2),
            "reason": reason,
            "explanation": explanation,
            "processing_days": "1–3 рабочих дня на карту плательщика",
        }
