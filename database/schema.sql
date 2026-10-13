-- ============================================================================
-- Litera — Cross-platform Online Bookstore
-- Database Schema Specification (PostgreSQL 16+)
-- Course: Human-Computer Interaction Design (HCI) / BSU FAMCS 2026
-- Authors: Kirill Zaidal, Anna-Maria Savitskaya (Group 12)
-- ============================================================================

-- 0. Extensions & Schema Configuration
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Clean-up existing objects in public schema (safe idempotency)
DROP TABLE IF EXISTS inventory_transactions CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS stock_items CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS order_status CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS payment_method CASCADE;
DROP TYPE IF EXISTS delivery_type CASCADE;
DROP TYPE IF EXISTS book_format CASCADE;
DROP TYPE IF EXISTS inventory_action CASCADE;

-- 1. Custom Types and Enums
CREATE TYPE user_role AS ENUM (
    'GUEST',
    'CUSTOMER',
    'WAREHOUSE_MANAGER',
    'CONTENT_MANAGER',
    'ADMIN'
);

CREATE TYPE order_status AS ENUM (
    'PENDING_PAYMENT',
    'PAID',
    'PROCESSING',
    'PACKED',
    'SHIPPED',
    'DELIVERED',
    'CANCELLED',
    'REFUNDED'
);

CREATE TYPE payment_status AS ENUM (
    'PENDING',
    'AUTHORIZED',
    'CAPTURED',
    'FAILED',
    'REFUNDED'
);

CREATE TYPE payment_method AS ENUM (
    'CARD_ONLINE',
    'SBP',
    'CASH_ON_DELIVERY',
    'BONUS_POINTS'
);

CREATE TYPE delivery_type AS ENUM (
    'COURIER',
    'PICKUP_BRANCH',
    'POSTAL_SERVICE'
);

CREATE TYPE book_format AS ENUM (
    'HARDCOVER',
    'PAPERBACK',
    'EBOOK',
    'AUDIOBOOK'
);

CREATE TYPE inventory_action AS ENUM (
    'RESTOCK',
    'RESERVE',
    'RELEASE_RESERVE',
    'DISPATCH',
    'WRITE_OFF',
    'AUDIT_ADJUSTMENT'
);

-- ============================================================================
-- 2. Tables Definition
-- ============================================================================

-- 2.1 Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    role user_role NOT NULL DEFAULT 'CUSTOMER',
    bonus_balance INT NOT NULL DEFAULT 0 CHECK (bonus_balance >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2.2 Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2.3 Books table
CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    discount_price NUMERIC(10, 2) CHECK (discount_price IS NULL OR (discount_price >= 0 AND discount_price <= price)),
    cover_url VARCHAR(500),
    preview_pdf_url VARCHAR(500),
    description TEXT,
    publication_year INT CHECK (publication_year BETWEEN 1000 AND 2100),
    pages INT CHECK (pages > 0),
    format book_format NOT NULL DEFAULT 'HARDCOVER',
    language VARCHAR(10) NOT NULL DEFAULT 'RU',
    rating NUMERIC(3, 2) NOT NULL DEFAULT 5.00 CHECK (rating >= 0.00 AND rating <= 5.00),
    reviews_count INT NOT NULL DEFAULT 0 CHECK (reviews_count >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2.4 Branches & Pickup Points table
CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Минск',
    phone VARCHAR(30),
    work_hours VARCHAR(100) NOT NULL DEFAULT '10:00 - 21:00',
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    is_warehouse BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2.5 Stock items per branch table
CREATE TABLE stock_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reserved INT NOT NULL DEFAULT 0 CHECK (reserved >= 0),
    shelf_location VARCHAR(50),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_book_branch UNIQUE (book_id, branch_id),
    CONSTRAINT chk_reserved_le_quantity CHECK (reserved <= quantity)
);

-- 2.6 Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) NOT NULL UNIQUE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    branch_id UUID REFERENCES branches(id) ON DELETE SET NULL,
    status order_status NOT NULL DEFAULT 'PENDING_PAYMENT',
    payment_method payment_method NOT NULL DEFAULT 'CARD_ONLINE',
    payment_status payment_status NOT NULL DEFAULT 'PENDING',
    items_total NUMERIC(10, 2) NOT NULL CHECK (items_total >= 0),
    delivery_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (delivery_cost >= 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    delivery_type delivery_type NOT NULL DEFAULT 'COURIER',
    delivery_address TEXT,
    contact_phone VARCHAR(20) NOT NULL,
    contact_name VARCHAR(150) NOT NULL,
    cancel_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2.7 Order items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2.8 Cart items table (supports both authenticated users and guest guest sessions)
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_user_or_session CHECK (user_id IS NOT NULL OR session_id IS NOT NULL)
);

-- 2.9 Reviews and Ratings table
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_book_review UNIQUE (user_id, book_id)
);

-- 2.10 Inventory audit transactions table
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_item_id UUID NOT NULL REFERENCES stock_items(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
    action inventory_action NOT NULL,
    delta_quantity INT NOT NULL DEFAULT 0,
    delta_reserved INT NOT NULL DEFAULT 0,
    performed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. Indexes for High-Performance Queries
-- ============================================================================

-- Fast lookup indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

CREATE INDEX idx_categories_slug ON categories(slug);

CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_category ON books(category_id);
CREATE INDEX idx_books_price ON books(price);
CREATE INDEX idx_books_rating ON books(rating DESC);
CREATE INDEX idx_books_is_active ON books(is_active);

-- Full-text search index on title, author, and description
CREATE INDEX idx_books_fts ON books USING gin (
    to_tsvector('russian', coalesce(title, '') || ' ' || coalesce(author, '') || ' ' || coalesce(description, ''))
);

CREATE INDEX idx_stock_items_book_branch ON stock_items(book_id, branch_id);
CREATE INDEX idx_stock_items_quantity ON stock_items(quantity);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_order_number ON orders(order_number);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_book_id ON order_items(book_id);

-- Unique items per user cart and per guest session cart
CREATE UNIQUE INDEX idx_cart_user_book ON cart_items(user_id, book_id) WHERE user_id IS NOT NULL;
CREATE UNIQUE INDEX idx_cart_session_book ON cart_items(session_id, book_id) WHERE session_id IS NOT NULL;
CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);
CREATE INDEX idx_cart_items_session_id ON cart_items(session_id);

CREATE INDEX idx_reviews_book_id ON reviews(book_id);

CREATE INDEX idx_inventory_tx_stock_item ON inventory_transactions(stock_item_id);
CREATE INDEX idx_inventory_tx_order ON inventory_transactions(order_id);

-- ============================================================================
-- 4. Stored Procedures and Triggers
-- ============================================================================

-- 4.1 Generic updated_at timestamp refresher
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_books_updated_at
BEFORE UPDATE ON books
FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_stock_items_updated_at
BEFORE UPDATE ON stock_items
FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_cart_items_updated_at
BEFORE UPDATE ON cart_items
FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

-- 4.2 Auto-generating unique order number (format: LIT-YYYYMMDD-XXXXX)
CREATE OR REPLACE FUNCTION fn_generate_order_number()
RETURNS TRIGGER AS $$
DECLARE
    seq_val TEXT;
BEGIN
    IF NEW.order_number IS NULL OR NEW.order_number = '' THEN
        seq_val := LPAD(FLOOR(RANDOM() * 100000)::TEXT, 5, '0');
        NEW.order_number := 'LIT-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || seq_val;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_generate_number
BEFORE INSERT ON orders
FOR EACH ROW EXECUTE FUNCTION fn_generate_order_number();

-- 4.3 Trigger to re-calculate book rating and review count
CREATE OR REPLACE FUNCTION fn_recalculate_book_rating()
RETURNS TRIGGER AS $$
DECLARE
    target_book_id UUID;
    avg_rate NUMERIC(3, 2);
    cnt INT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_book_id := OLD.book_id;
    ELSE
        target_book_id := NEW.book_id;
    END IF;

    SELECT COALESCE(ROUND(AVG(rating), 2), 5.00), COUNT(*)
    INTO avg_rate, cnt
    FROM reviews
    WHERE book_id = target_book_id;

    UPDATE books
    SET rating = avg_rate,
        reviews_count = cnt,
        updated_at = NOW()
    WHERE id = target_book_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_reviews_rating_insert
AFTER INSERT OR UPDATE ON reviews
FOR EACH ROW EXECUTE FUNCTION fn_recalculate_book_rating();

CREATE TRIGGER trg_reviews_rating_delete
AFTER DELETE ON reviews
FOR EACH ROW EXECUTE FUNCTION fn_recalculate_book_rating();

-- ============================================================================
-- 5. Demonstration Seed Data
-- ============================================================================

-- 5.1 Categories
INSERT INTO categories (id, name, slug, description) VALUES
('11111111-1111-1111-1111-111111111101', 'Программирование и IT', 'it-and-programming', 'Литература по разработке ПО, архитектуре, базам данных и алгоритмам'),
('11111111-1111-1111-1111-111111111102', 'Художественная литература', 'fiction', 'Мировая и отечественная классика, современная проза'),
('11111111-1111-1111-1111-111111111103', 'Научная фантастика', 'science-fiction', 'Космическая фантастика, антиутопии и научные романы'),
('11111111-1111-1111-1111-111111111104', 'Психология и продуктивность', 'psychology', 'Книги по психологии личности, тайм-менеджменту и переговорам');

-- 5.2 Users
INSERT INTO users (id, email, password_hash, full_name, phone, role, bonus_balance) VALUES
('22222222-2222-2222-2222-222222222201', 'admin@litera.by', '$2a$12$e8Y...AdminHashedPassword...', 'Кирилл Зайдаль (Администратор)', '+375291234567', 'ADMIN', 1000),
('22222222-2222-2222-2222-222222222202', 'warehouse@litera.by', '$2a$12$e8Y...WarehouseHashedPassword...', 'Алексей Смирнов (Склад)', '+375297654321', 'WAREHOUSE_MANAGER', 200),
('22222222-2222-2222-2222-222222222203', 'customer@litera.by', '$2a$12$e8Y...CustomerHashedPassword...', 'Анна-Мария Савицкая (Покупатель)', '+375449876543', 'CUSTOMER', 350);

-- 5.3 Branches
INSERT INTO branches (id, name, address, city, phone, work_hours, latitude, longitude, is_warehouse) VALUES
('33333333-3333-3333-3333-333333333301', 'Центральный хаб «Платонова»', 'ул. Платонова, 39', 'Минск', '+375172001122', '08:00 - 20:00', 53.911470, 27.595430, TRUE),
('33333333-3333-3333-3333-333333333302', 'Филиал «ТЦ Галерея»', 'пр-т Победителей, 9', 'Минск', '+375173002233', '10:00 - 22:00', 53.908520, 27.548860, FALSE),
('33333333-3333-3333-3333-333333333303', 'Филиал «ТЦ Dana Mall»', 'ул. Петра Мстиславца, 11', 'Минск', '+375174003344', '10:00 - 22:00', 53.933320, 27.652150, FALSE);

-- 5.4 Books
INSERT INTO books (id, isbn, title, author, category_id, price, discount_price, cover_url, preview_pdf_url, description, publication_year, pages, format, rating, reviews_count) VALUES
('44444444-4444-4444-4444-444444444401', '978-5-4461-0923-4', 'Чистый код: создание, анализ и рефакторинг', 'Роберт Мартин', '11111111-1111-1111-1111-111111111101', 65.50, 58.90, 'https://cdn.litera.by/covers/clean-code.jpg', 'https://cdn.litera.by/previews/clean-code-preview.pdf', 'Классическое руководство по написанию чистого, расширяемого и поддерживаемого программного кода.', 2023, 464, 'HARDCOVER', 4.90, 42),
('44444444-4444-4444-4444-444444444402', '978-5-4461-1287-6', 'Паттерны микросервисной архитектуры', 'Крис Ричардсон', '11111111-1111-1111-1111-111111111101', 82.00, NULL, 'https://cdn.litera.by/covers/microservices-patterns.jpg', 'https://cdn.litera.by/previews/microservices-preview.pdf', 'Исчерпывающее руководство по декомпозиции монолитов, паттернам Saga, CQRS и распределенным транзакциям.', 2022, 544, 'HARDCOVER', 4.85, 28),
('44444444-4444-4444-4444-444444444403', '978-5-17-090835-6', 'Мастер и Маргарита', 'Михаил Булгаков', '11111111-1111-1111-1111-111111111102', 32.40, 29.00, 'https://cdn.litera.by/covers/master-margarita.jpg', 'https://cdn.litera.by/previews/master-margarita-preview.pdf', 'Культовый роман мировой классики с мистическим сюжетом и глубоким философским подтекстом.', 2021, 512, 'HARDCOVER', 4.95, 115),
('44444444-4444-4444-4444-444444444404', '978-5-17-080115-2', '1984', 'Джордж Оруэлл', '11111111-1111-1111-1111-111111111103', 24.50, NULL, 'https://cdn.litera.by/covers/1984.jpg', 'https://cdn.litera.by/previews/1984-preview.pdf', 'Бессмертный роман-антиутопия о тотальном контроле, свободе мысли и природе власти.', 2022, 320, 'PAPERBACK', 4.90, 89),
('44444444-4444-4444-4444-444444444405', '978-5-04-099344-4', 'Атомные привычки', 'Джеймс Клир', '11111111-1111-1111-1111-111111111104', 38.00, 34.20, 'https://cdn.litera.by/covers/atomic-habits.jpg', 'https://cdn.litera.by/previews/atomic-habits-preview.pdf', 'Простая и доказанная методика формирования полезных привычек и избавления от деструктивных.', 2023, 304, 'HARDCOVER', 4.80, 76);

-- 5.5 Stock Items
INSERT INTO stock_items (id, book_id, branch_id, quantity, reserved, shelf_location) VALUES
('55555555-5555-5555-5555-555555555501', '44444444-4444-4444-4444-444444444401', '33333333-3333-3333-3333-333333333301', 35, 2, 'A-12-04'),
('55555555-5555-5555-5555-555555555502', '44444444-4444-4444-4444-444444444401', '33333333-3333-3333-3333-333333333302', 5, 0, 'S-02-11'),
('55555555-5555-5555-5555-555555555503', '44444444-4444-4444-4444-444444444402', '33333333-3333-3333-3333-333333333301', 20, 1, 'A-14-02'),
('55555555-5555-5555-5555-555555555504', '44444444-4444-4444-4444-444444444403', '33333333-3333-3333-3333-333333333302', 12, 1, 'B-01-05'),
('55555555-5555-5555-5555-555555555505', '44444444-4444-4444-4444-444444444404', '33333333-3333-3333-3333-333333333303', 18, 0, 'C-05-09'),
('55555555-5555-5555-5555-555555555506', '44444444-4444-4444-4444-444444444405', '33333333-3333-3333-3333-333333333301', 40, 3, 'D-08-01');

-- 5.6 Orders
INSERT INTO orders (id, order_number, user_id, branch_id, status, payment_method, payment_status, items_total, delivery_cost, total_price, delivery_type, delivery_address, contact_phone, contact_name) VALUES
('66666666-6666-6666-6666-666666666601', 'LIT-20261013-10001', '22222222-2222-2222-2222-222222222203', '33333333-3333-3333-3333-333333333302', 'PROCESSING', 'CARD_ONLINE', 'CAPTURED', 58.90, 0.00, 58.90, 'PICKUP_BRANCH', 'Самовывоз из ТЦ Галерея', '+375449876543', 'Анна-Мария Савицкая'),
('66666666-6666-6666-6666-666666666602', 'LIT-20261012-10002', '22222222-2222-2222-2222-222222222203', NULL, 'DELIVERED', 'SBP', 'CAPTURED', 114.40, 5.00, 119.40, 'COURIER', 'г. Минск, пр-т Независимости, 4, кв. 12', '+375449876543', 'Анна-Мария Савицкая');

-- 5.7 Order Items
INSERT INTO order_items (id, order_id, book_id, quantity, unit_price, total_price) VALUES
('77777777-7777-7777-7777-777777777701', '66666666-6666-6666-6666-666666666601', '44444444-4444-4444-4444-444444444401', 1, 58.90, 58.90),
('77777777-7777-7777-7777-777777777702', '66666666-6666-6666-6666-666666666602', '44444444-4444-4444-4444-444444444402', 1, 82.00, 82.00),
('77777777-7777-7777-7777-777777777703', '66666666-6666-6666-6666-666666666602', '44444444-4444-4444-4444-444444444403', 1, 32.40, 32.40);
