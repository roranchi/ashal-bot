from typing import Dict

MAINTENANCE_TEMPLATES: Dict[str, Dict[str, str]] = {
    'ar': {
        'emergency': "تسريب ماء | عطل كهربائي",
        'urgent': "عطل تكييف | أعطال أمنية",
        'normal': "أعطال عامة | طلاء",
        'new_assignment': "مهمة جديدة #{ticket_id} - {issue_type}",
        'status_update': "تحديث حالة #{ticket_id} إلى {status}",
        'completion': "تم إكمال #{ticket_id} بنجاح"
    },
    'en': {
        'emergency': "Water Leak | Electrical Issue",
        'urgent': "AC Problem | Security Issues",
        'normal': "General Maintenance | Painting",
        'new_assignment': "New assignment #{ticket_id} - {issue_type}",
        'status_update': "Updated #{ticket_id} to {status}",
        'completion': "Completed #{ticket_id} successfully"
    }
}

def get_template(lang: str, key: str, params: Dict) -> str:
    return MAINTENANCE_TEMPLATES.get(lang, MAINTENANCE_TEMPLATES['en'])[key].format(**params)
