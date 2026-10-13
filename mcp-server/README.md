# Litera MCP Server (Model Context Protocol)

Сервер контекстного протокола **Model Context Protocol (MCP)** для кроссплатформенного книжного онлайн-магазина **«Litera»**. Разработан в рамках Лабораторной работы №4 по дисциплине *«Проектирование человеко-машинных интерфейсов»* (БГУ ФПМИ, 2026 г., авторы: Зайдаль Кирилл, Савицкая Анна-Мария, группа 12).

MCP-сервер позволяет подключать большую языковую модель (LLM: Claude, GPT-4, Gemini) напрямую к сервисам Litera в качестве интеллектуального агента. Модель получает доступ к инструментам оформления покупок, актуальному контексту каталога и шаблонам взаимодействия.

---

## Архитектура и поддерживаемый функционал

Протокол взаимодействия: **JSON-RPC 2.0 over standard I/O (stdio)**, спецификация MCP **2024-11-05**.
Сервер реализован на Python и оснащен встроенным mock-хранилищем на базе SQLite, инициализирующимся доменными сущностями из `schema.sql` (книги, остатки в филиалах, заказы, пользователи).

### 1. Инструменты (Tools)
| Инструмент | Назначение | Параметры |
|---|---|---|
| `search_books` | Интеллектуальный поиск книг по названию, автору, ISBN, категории и максимальной цене | `query`, `category`, `max_price`, `limit` |
| `check_inventory` | Проверка складских остатков книги по всем филиалам сети и распределительному хабу | `book_id` (UUID или ISBN), `branch_id` (опционально) |
| `create_order` | Оформление нового заказа, резервирование остатков и расчет стоимости доставки | `user_id`, `items`, `delivery_type`, `delivery_address`, `branch_id`, `contact_phone`, `contact_name`, `payment_method` |
| `cancel_order` | Отмена заказа с валидацией логистического статуса и возвратом остатков на склад | `order_id` (UUID или номер), `reason` |

> **Бизнес-правило отмены:** Если заказ находится на этапах `SHIPPED` (передан курьеру/в доставку) или `DELIVERED` (вручен), отмена через `cancel_order` блокируется с возвратом ошибки `ORDER_CANCELLATION_CONFLICT`. Клиенту предлагается регламент возврата товара через промпт `refund_calculation`.

### 2. Ресурсы (Resources)
| URI / Шаблон | Название | MIME Type | Содержимое |
|---|---|---|---|
| `books://catalog` | Каталог книг | `application/json` | Полный список доступных изданий с ценами, рейтингами и остатками |
| `orders://recent` | Недавние заказы | `application/json` | Список последних 10 оформленных заказов в системе |
| `orders://user/{id}/history` | История заказов пользователя | `application/json` | Персональная история заказов клиента по его UUID или email |

### 3. Промпты (Prompts)
| Название | Назначение | Аргументы |
|---|---|---|
| `order_assistance` | Интеллектуальный консультант по подбору книг и оформлению корзины под интересы покупателя | `preferences` (обяз.), `budget`, `user_id` |
| `refund_calculation` | Расчет финансовой компенсации, удержания доставки и сроков возврата средств при отмене заказа | `order_id` (обяз.), `reason` (обяз.) |

---

## Установка и запуск

### Требования
- Python 3.9 или выше.
- Внешние зависимости не требуются для работы автономного stdio-сервера (используются стандартные библиотеки `sqlite3`, `json`, `sys`, `unittest`).

### 1. Запуск модульных тестов
```bash
cd Litera/mcp-server
python3 -m unittest test_mcp.py -v
```
Все 37 тестов (хранилище, валидации, регистронезависимый поиск кириллицы, толерантность ISBN, инструменты, ресурсы, промпты, JSON-RPC протокол) выполняются без ошибок.

### 2. Автономный запуск сервера через консоль
```bash
python3 server.py
```
После запуска сервер ожидает входящих JSON-RPC сообщений в стандартный поток ввода (`stdin`) и отвечает в стандартный поток вывода (`stdout`). Диагностические логи пишутся в `stderr`.

---

## Тестирование через MCP Inspector

Официальный инструмент визуального тестирования [MCP Inspector](https://github.com/modelcontextprotocol/inspector) позволяет интерактивно вызывать инструменты и просматривать ресурсы:

```bash
npx @modelcontextprotocol/inspector python3 /полный/путь/к/Litera/mcp-server/server.py
```

После запуска откройте в браузере предоставленный адрес `http://localhost:5173`. Вы сможете:
1. Выбрать вкладку **Tools** и нажать `search_books` с аргументом `{"query": "чистый код"}`.
2. Проверить инструмент `create_order` и убедиться в успешном резервировании книги на складе.
3. Протестировать инструмент `cancel_order` на заказе `LIT-20261012-10002` и увидеть корректный перехват ошибки запрета отмены доставленного заказа.
4. Открыть вкладку **Resources** и прочитать `books://catalog`.
5. Во вкладке **Prompts** запустить генерацию промпта `order_assistance`.

---

## Подключение к Claude Desktop

Добавьте конфигурацию MCP-сервера в файл конфигурации Claude Desktop:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "litera-bookstore": {
      "command": "python3",
      "args": [
        "/Users/kirill/Documents/projects/пчми/Litera/mcp-server/server.py"
      ]
    }
  }
}
```

После перезапуска приложения в интерфейсе Claude появится значок молотка (Tools) со списком доступных инструментов книжного магазина Litera.

---

## Пример прямого JSON-RPC диалога

### 1. Рукопожатие инициализации
**Запрос (stdin):**
```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
```
**Ответ (stdout):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": false},
      "resources": {"subscribe": false, "listChanged": false},
      "prompts": {"listChanged": false}
    },
    "serverInfo": {
      "name": "litera-bookstore-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

### 2. Вызов инструмента `check_inventory`
**Запрос (stdin):**
```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "check_inventory", "arguments": {"book_id": "978-5-4461-0923-4"}}}
```
**Ответ (stdout):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"book_id\": \"44444444-4444-4444-4444-444444444401\",\n  \"title\": \"Чистый код: создание, анализ и рефакторинг\",\n  \"author\": \"Роберт Мартин\",\n  \"total_available\": 38,\n  \"branches\": [\n    {\n      \"branch_name\": \"Центральный хаб «Платонова»\",\n      \"quantity\": 35,\n      \"reserved\": 2,\n      \"available\": 33,\n      \"shelf_location\": \"A-12-04\"\n    },\n    {\n      \"branch_name\": \"Филиал «ТЦ Галерея»\",\n      \"quantity\": 5,\n      \"reserved\": 0,\n      \"available\": 5,\n      \"shelf_location\": \"S-02-11\"\n    }\n  ]\n}"
      }
    ],
    "isError": false
  }
}
```
