import re
from supabase import Client
from typing import Dict
from templates.maintenance_templates import get_template as get_maintenance_template

KEYWORDS_MAP = {
    'leak': 'emergency',
    'تسريب': 'emergency',
    'water': 'emergency',
    'ماء': 'emergency',
    'electric': 'emergency',
    'كهرباء': 'emergency',
    'ac': 'urgent',
    'تكييف': 'urgent',
    'security': 'urgent',
    'أمن': 'urgent'
}

def process_whatsapp_message(supabase: Client, message: str, phone: str) -> Dict:
    try:
        tenant_data = supabase.table('tenants').select('id, language_preference').eq('phone', phone).execute()
        if not tenant_data.data:
            return {'response': 'لم يتم العثور على مستأجر بهذا الرقم', 'language': 'ar'}
        
        tenant = tenant_data.data[0]
        lang = tenant.get('language_preference', 'ar')
        message_lower = message.lower()
        
        for key, category in KEYWORDS_MAP.items():
            if re.search(key, message_lower, re.IGNORECASE):
                maintenance_data = {
                    'category': category,
                    'description': message,
                    'tenant_id': tenant['id'],
                    'status': 'open'
                }
                result = supabase.table('maintenance_requests').insert(maintenance_data).execute()
                if result.data:
                    ticket_id = result.data[0]['id']
                    return {
                        'category': category,
                        'description': message,
                        'tenant_id': tenant['id'],
                        'language': lang,
                        'response': get_maintenance_template(lang, 'new_assignment', {
                            'ticket_id': ticket_id,
                            'issue_type': category
                        })
                    }
        
        return {
            'response': 'شكراً لتواصلكم. سنقوم بمعالجة طلبكم قريباً.',
            'language': lang
        }
        
    except Exception as e:
        return {'response': 'حدث خطأ في معالجة الرسالة', 'language': 'ar'}
