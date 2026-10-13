"""
Litera MCP Server — Resources Implementation
Implements MCP resources:
- books://catalog
- orders://recent
- orders://user/{id}/history (Resource template)
"""

from __future__ import annotations

import json
import re
from urllib.parse import unquote
from typing import Any, Dict, List, Optional, Tuple
from storage import LiteraStorage, StorageError


def get_resource_definitions() -> Dict[str, Any]:
    return {
        "resources": [
            {
                "uri": "books://catalog",
                "name": "Каталог книг Litera",
                "description": "Полный актуальный реестр доступных изданий с ценами, остатками и рейтингами",
                "mimeType": "application/json",
            },
            {
                "uri": "orders://recent",
                "name": "Недавние заказы магазина",
                "description": "Оперативный реестр последних оформленных заказов для мониторинга",
                "mimeType": "application/json",
            },
        ],
        "resourceTemplates": [
            {
                "uriTemplate": "orders://user/{id}/history",
                "name": "История заказов покупателя",
                "description": "Персональная хронология покупок пользователя по его идентификатору или email",
                "mimeType": "application/json",
            }
        ],
    }


def read_resource(storage: LiteraStorage, uri: str) -> Dict[str, Any]:
    """
    Reads resource by URI. Returns MCP format:
    {"contents": [{"uri": uri, "mimeType": "application/json", "text": "..."}]}
    """
    if uri == "books://catalog":
        catalog = storage.get_catalog()
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({"total_titles": len(catalog), "catalog": catalog}, ensure_ascii=False, indent=2),
                }
            ]
        }

    elif uri == "orders://recent":
        orders = storage.get_recent_orders(limit=10)
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({"count": len(orders), "recent_orders": orders}, ensure_ascii=False, indent=2),
                }
            ]
        }

    # Match URI template: orders://user/{id}/history
    user_match = re.match(r"^orders://user/([^/]+)/history$", uri)
    if user_match:
        user_id = unquote(user_match.group(1))
        history = storage.get_user_order_history(user_id=user_id)
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(
                        {"user_id": user_id, "orders_count": len(history), "orders": history},
                        ensure_ascii=False,
                        indent=2,
                    ),
                }
            ]
        }

    raise StorageError(f"Ресурс с URI '{uri}' не поддерживается сервером Litera MCP")
