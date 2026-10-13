# Litera

## Description
Litera — кроссплатформенный книжный онлайн-магазин, предназначенный для подбора, покупки и отслеживания доставки печатных и электронных изданий. Платформа включает полнофункциональный веб-сервис и нативное мобильное приложение с каталогом, тематическими фильтрами, поиском по авторам/издательствам, чтением ознакомительных фрагментов и оформлением предзаказов. Для персонала реализована панель управления заказами, учёта складских остатков и администрирования карточек книг. Проект разрабатывается в рамках курса «Проектирование человеко-машинных интерфейсов» (ФПМИ БГУ, 2026 г.).

---

## Архитектура и структура проекта

```text
Litera/
├── api/
│   └── openapi.yaml           # Спецификация REST API в формате OpenAPI 3.0.3 (22 эндпоинта)
├── database/
│   └── schema.sql             # Физическая схема базы данных PostgreSQL 16+ (DDL, индексы, триггеры, seed)
├── docs/
│   ├── index.md               # Главная страница отчетов на GitHub Pages
│   ├── lab1.md                # ЛР №1: Исследование пользователей и предметной области
│   ├── lab2.md                # ЛР №2: Проектирование информационной архитектуры
│   ├── lab3.md                # ЛР №3: Разработка требований и архитектурная спецификация (C4, UML, EventStorming)
│   ├── lab4.md                # ЛР №4: Стили интеграции программных систем и проектирование API
│   └── images/                # Векторные и растровые иллюстрации диаграмм
├── mcp-server/                # Model Context Protocol (MCP) сервер интеграции с LLM
│   ├── server.py              # Точка входа stdio JSON-RPC 2.0 сервера
│   ├── storage.py             # Репозиторий данных (SQLite / in-memory)
│   ├── tools.py               # Инструменты: search_books, create_order, cancel_order, check_inventory
│   ├── resources.py           # Ресурсы: books://catalog, orders://recent, orders://user/{id}/history
│   ├── prompts.py             # Промпты: order_assistance, refund_calculation
│   ├── test_mcp.py            # Набор из 37 модульных тестов
│   ├── pyproject.toml         # Метаданные пакета Python
│   ├── requirements.txt       # Зависимости MCP-сервера
│   └── README.md              # Документация по запуску и подключению к Claude / Inspector
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI: линтинг, тесты, валидация OpenAPI и Docker
├── Dockerfile                 # Многоэтапный Dockerfile для бэкенда и MCP
├── docker-compose.yml         # Оркестрация: PostgreSQL 16, Redis 7, Prism Mock, Swagger UI, MCP Server
└── README.md
```

---

## Подмодули системы (Submodules)

* **Litera-Web** — фронтенд-приложение онлайн-магазина на React (каталог, веб-ридер, корзина, оформление заказов).
* **Litera-Server** — серверная часть, бизнес-логика обработки заказов, REST API и интеграции.
* **Litera-Mobile** — мобильный клиент книжного магазина на React Native для iOS и Android.

---

## Установка и локальный запуск

### 1. Клонирование репозитория
```bash
git clone --recurse-submodules https://github.com/fpmi-hci-2026/Litera.git
cd Litera
```

Если репозиторий уже склонирован без флага `--recurse-submodules`:
```bash
git submodule update --init --recursive
```

### 2. Запуск инфраструктуры через Docker Compose
Запуск полного стека (PostgreSQL, Redis, Prism API Mock, Swagger UI, MCP Server):
```bash
docker compose up -d
```

Сервисы будут доступны по адресам:
* **Интерактивная Swagger UI документация:** [http://localhost:8080](http://localhost:8080)
* **REST API Mock-сервер (Prism):** [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
* **База данных PostgreSQL:** `localhost:5432` (`user: litera_user`, `db: litera_db`)
* **Кэш Redis:** `localhost:6379`

### 3. Запуск и тестирование MCP-сервера (Model Context Protocol)
Для подключения LLM-агентов (Claude Desktop, Cursor, MCP Inspector):
```bash
cd mcp-server

# Запуск полного набора тестов
python3 -m unittest test_mcp.py -v

# Запуск визуального инспектора MCP
npx @modelcontextprotocol/inspector python3 server.py
```

Подробные инструкции по настройке `claude_desktop_config.json` приведены в [`mcp-server/README.md`](./mcp-server/README.md).

---

## Документация и отчеты

Полные академические отчеты по проектированию опубликованы на GitHub Pages:
**[https://fpmi-hci-2026.github.io/Litera/](https://fpmi-hci-2026.github.io/Litera/)**

* [Отчет по лабораторной работе №1](./docs/lab1.md)
* [Отчет по лабораторной работе №2](./docs/lab2.md)
* [Отчет по лабораторной работе №3](./docs/lab3.md)
* [Отчет по лабораторной работе №4](./docs/lab4.md)

---

## Участники проекта (Contributing)

* **Зайдаль Кирилл Андреевич (группа 12):** Проектирование физической модели базы данных PostgreSQL 16, написание DDL-скрипта `schema.sql`, ERD-диаграммы (PlantUML, Mermaid), разработка Model Context Protocol (MCP) сервера, написание тестового набора `test_mcp.py`, проектирование `Dockerfile` и `docker-compose.yml`, интеграционная сборка проекта, релизный деплой и публикация артефактов в репозиторий GitHub.
* **Савицкая Анна-Мария Алексеевна (группа 12):** Разработка модели требований и реестра вариантов использования (трассировка Actor $\rightarrow$ US $\rightarrow$ UC), проектирование маршрутов и контрактов REST API, разработка спецификации OpenAPI 3.0 (`openapi.yaml`), подготовка инструкций по тестированию в Postman/Bruno, проектирование и настройка сценариев непрерывной интеграции (CI-пайплайн GitHub Actions).
