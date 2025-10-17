from typing import Dict

PAYMENT_TEMPLATES: Dict[str, Dict[str, str]] = {
    'ar': {
        'reminder': "تذكير: دفعة #{payment_id} بقيمة {amount} مستحقة بتاريخ {due_date}",
        'overdue': "تنبيه: دفعة #{payment_id} بقيمة {amount} متأخرة منذ {due_date}"
    },
    'en': {
        'reminder': "Reminder: Payment #{payment_id} of {amount} is due on {due_date}",
        'overdue': "Alert: Payment #{payment_id} of {amount} is overdue since {due_date}"
    }
}

def get_template(lang: str, key: str, params: Dict) -> str:
    return PAYMENT_TEMPLATES.get(lang, PAYMENT_TEMPLATES['en'])[key].format(**params)
