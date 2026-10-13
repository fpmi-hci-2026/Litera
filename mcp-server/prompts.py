"""
Litera MCP Server — Prompts Implementation
Implements MCP prompts:
- order_assistance
- refund_calculation
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from storage import LiteraStorage, StorageError


def get_prompt_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "order_assistance",
            "description": "Интеллектуальный консультант по подбору литературы и формированию заказа на основе предпочтений покупателя.",
            "arguments": [
                {
                    "name": "preferences",
                    "description": "Жанровые или тематические интересы покупателя (например 'книги по чистой архитектуре и микросервисам')",
                    "required": True,
                },
                {
                    "name": "budget",
                    "description": "Максимальный бюджет в BYN (например '150')",
                    "required": False,
                },
                {
                    "name": "user_id",
                    "description": "Email или UUID зарегистрированного пользователя для учета персональной скидки",
                    "required": False,
                },
            ],
        },
        {
            "name": "refund_calculation",
            "description": "Расчет суммы возврата денежных средств, удержания логистических расходов и регламента при отмене/возврате заказа.",
            "arguments": [
                {
                    "name": "order_id",
                    "description": "Идентификатор заказа или номер (например 'LIT-20261013-10001' или '66666666-6666-6666-6666-666666666601')",
                    "required": True,
                },
                {
                    "name": "reason",
                    "description": "Причина оформления возврата покупателем",
                    "required": True,
                },
            ],
        },
    ]


def render_prompt(storage: LiteraStorage, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renders prompt into MCP prompt response:
    {"description": "...", "messages": [{"role": "user", "content": {"type": "text", "text": "..."}}]}
    """
    if name == "order_assistance":
        preferences = arguments.get("preferences", "")
        budget = arguments.get("budget")
        user_id = arguments.get("user_id")
        max_price_val = None
        if budget:
            try:
                max_price_val = float(str(budget).replace(",", ".").strip())
            except ValueError:
                pass

        catalog = storage.search_books(
            query=preferences if len(preferences) < 30 else None,
            max_price=max_price_val,
            limit=5,
        )
        catalog_sample = json.dumps(catalog, ensure_ascii=False, indent=2)

        prompt_text = (
            f"Вы — консультант книжного онлайн-магазина «Litera».\n\n"
            f"Запрос покупателя:\n"
            f"- Тематические предпочтения: {preferences}\n"
            f"- Доступный бюджет: {budget if budget else 'Не ограничен'} BYN\n"
            f"- Идентификатор клиента: {user_id if user_id else 'Гость витрины'}\n\n"
            f"Актуальные книги из каталога Litera по данной тематике:\n"
            f"{catalog_sample}\n\n"
            f"Инструкции для ассистента:\n"
            f"1. Поприветствуйте читателя в стиле книжного клуба Litera.\n"
            f"2. Предложите топ-2 или 3 наиболее релевантных издания из каталога выше.\n"
            f"3. Обоснуйте ценность каждой книги, укажите автора, формат и актуальную цену.\n"
            f"4. Проверьте остатки с помощью инструмента 'check_inventory' и предложите способ доставки.\n"
            f"5. Предложите оформить заказ через инструмент 'create_order'."
        )

        return {
            "description": f"Ассистент по подбору книг по теме '{preferences}'",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text,
                    },
                }
            ],
        }

    elif name == "refund_calculation":
        order_id = arguments.get("order_id", "")
        reason = arguments.get("reason", "")
        if not order_id:
            raise StorageError("Параметр 'order_id' обязателен для расчета возврата")

        refund_calc = storage.calculate_refund(order_id=order_id, reason=reason)
        calc_json = json.dumps(refund_calc, ensure_ascii=False, indent=2)

        prompt_text = (
            f"Вы — специалист службы клиентской поддержки и возвратов книжного магазина «Litera».\n\n"
            f"Справка по заказу и расчету финансового возврата:\n"
            f"{calc_json}\n\n"
            f"Инструкция оператору:\n"
            f"1. Вежливо разъясните покупателю регламент возврата средств согласно Закону о защите прав потребителей.\n"
            f"2. Сообщите точную сумму к возврату ({refund_calc['refundable_amount']} BYN).\n"
            f"3. Если стоимость доставки удержана, поясните причину (логистический этап '{refund_calc['current_status']}').\n"
            f"4. Укажите регламентные сроки перечисления средств ({refund_calc['processing_days']}).\n"
            f"5. Предложите зачисление суммы на бонусный баланс для мгновенных покупок без ожидания межбанковского клиринга."
        )

        return {
            "description": f"Расчет возврата средств по заказу '{order_id}'",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text,
                    },
                }
            ],
        }

    raise StorageError(f"Промпт с именем '{name}' не зарегистрирован на сервере")
