import argparse
#!/usr/bin/env python3
"""
Smart Project Guardian Ultra - النسخة المطورة مع تكامل كامل للمواصفات
إصدار 2.0.0 - مع دعم API، إشعارات، وتكامل Supabase متقدم
"""

import os
import sys
import json
import logging
import random
import asyncio
import aiohttp
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from supabase import create_client, Client
except ImportError:
    Client = None

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    FastAPI = None

@dataclass
class Issue:
    """تمثيل موحد للمشكلة"""
    id: str
    type: str  # 'error', 'warning', 'info'
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    confidence: float = 0.8  # درجة الثقة من 0-1
    tags: List[str] = None
    solution: str = ""
    created_at: str = ""
    resolved: bool = False

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class NotificationManager:
    """مدير الإشعارات المتقدم"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.telegram_bot_token = config.get('telegram_bot_token')
        self.telegram_chat_id = config.get('telegram_chat_id')
        
    async def send_telegram(self, message: str) -> bool:
        """إرسال إشعار عبر Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logging.error(f"فشل إرسال إشعار Telegram: {e}")
            return False
    
    async def send_webhook(self, data: Dict) -> bool:
        """إرسال إشعار عبر Webhook"""
        webhook_url = self.config.get('webhook_url')
        if not webhook_url:
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=data) as response:
                    return response.status == 200
        except Exception as e:
            logging.error(f"فشل إرسال Webhook: {e}")
            return False

class LearningEngine:
    """محرك التعلم للتقليل من الإنذارات الكاذبة"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.issue_patterns = {}
        self.false_positives = set()
        
    async def load_historical_data(self):
        """تحميل البيانات التاريخية للتعلم"""
        try:
            # جلب المشكلات السابقة
            result = self.supabase.table('issues').select('*').execute()
            if result.data:
                for issue in result.data:
                    issue_key = self._generate_issue_key(issue)
                    if issue.get('resolved'):
                        self.false_positives.add(issue_key)
        except Exception as e:
            logging.warning(f"تعذر تحميل البيانات التاريخية: {e}")
    
    def _generate_issue_key(self, issue: Dict) -> str:
        """إنشاء مفتاح فريد للمشكلة"""
        return f"{issue.get('type')}:{issue.get('title')}:{issue.get('file_path', '')}"
    
    def should_alert(self, issue: Issue) -> bool:
        """تحديد إذا كان يجب إرسال تنبيه للمشكلة"""
        issue_key = self._generate_issue_key(asdict(issue))
        
        # تجاهل الإنذارات الكاذبة المعروفة
        if issue_key in self.false_positives:
            return False
            
        # زيادة العتبة للمشكلات منخفضة الثقة
        if issue.confidence < 0.6:
            return False
            
        return True
    
    def mark_false_positive(self, issue: Issue):
        """تحديد مشكلة كإنذار كاذب"""
        issue_key = self._generate_issue_key(asdict(issue))
        self.false_positives.add(issue_key)

class SmartProjectGuardianUltra:
    """الإصدار المطور من الحارس مع كل الميزات"""
    
    def __init__(self, project_path: str = '/opt/ashal-bot/', supabase_url: str = None, supabase_key: str = None):
        self.project_path = Path(project_path)
        self.reports_dir = self.project_path / 'guardian_reports'
        self.config_file = self.project_path / 'guardian_config.json'
        self.progress_file = self.project_path / 'daily_progress.json'
        self.log_file = self.project_path / 'guardian.log'
        
        # إعداد Supabase
        self.supabase = None
        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
            except Exception as e:
                logging.error(f"فشل تهيئة Supabase: {e}")

        self.reports_dir.mkdir(exist_ok=True)
        self._setup_logging()
        
        # تحميل التكوين
        self.config = self.load_config()
        
        # إدارة المكونات
        self.notification_manager = NotificationManager(self.config)
        self.learning_engine = LearningEngine(self.supabase) if self.supabase else None
        
        # حالة النظام
        self.project_name = self.config.get('project_name', 'Ashal WhatsApp Bot')
        self.energy_level = 'متوسط'
        self.current_issues: List[Issue] = []
        self.ws_clients = []
        self.agent_id = f"guardian_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # إحصائيات
        self.project_stats = {
            'total_files': 0,
            'python_files': 0,
            'last_scan': None,
            'issues_count': 0,
            'false_positives_count': 0
        }
        

    def _setup_logging(self):
        """إعداد نظام التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Dict:
        """تحميل التكوين"""
        default_config = {
            'project_name': 'Ashal WhatsApp Bot',
            'version': '2.0.0-Ultra',
            'setup_date': datetime.now().isoformat(),
            'scan_interval': 300,  # 5 دقائق
            'max_issues_per_scan': 50,
            'notification_enabled': True,
            'telegram_bot_token': '',
            'telegram_chat_id': '',
            'webhook_url': '',
            'api_endpoint': 'http://localhost:8000/v1'
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الإعدادات: {e}")
        
        # حفظ التكوين المحدث
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
            
        return default_config

    async def initialize_system(self):
        """تهيئة النظام"""
        self.logger.info("🛡️ بدء تشغيل Smart Project Guardian Ultra...")
        
        if self.learning_engine:
            await self.learning_engine.load_historical_data()
            
        # بدء المراقبة التلقائية
        asyncio.create_task(self.auto_monitoring_loop())

    async def auto_monitoring_loop(self):
        """حلقة المراقبة التلقائية"""
        while True:
            try:
                await self.run_comprehensive_scan()
                interval = self.config.get('scan_interval', 300)
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"خطأ في المراقبة التلقائية: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة ثم إعادة المحاولة

    async def run_comprehensive_scan(self):
        """مسح شامل للمشروع"""
        self.logger.info("بدء المسح الشامل للمشروع...")
        
        # إعادة تعيين الإحصائيات
        self.current_issues.clear()
        
        # تنفيذ الفحوصات
        await self.scan_project_structure()
        await self.check_environment_variables()
        await self.check_dependencies()
        await self.check_supabase_connection()
        await self.analyze_code_quality()
        
        # تطبيق التعلم على النتائج
        await self.apply_learning_filters()
        
        # إرسال التقارير والإشعارات
        await self.send_scan_report()
        
        self.project_stats['last_scan'] = datetime.now().isoformat()
        self.project_stats['issues_count'] = len(self.current_issues)
        
        self.logger.info(f"تم المسح الشامل: {len(self.current_issues)} مشكلة مكتشفة")

    async def scan_project_structure(self):
        """مسح هيكل المشروع"""
        self.project_stats.update({'total_files': 0, 'python_files': 0})
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                self.project_stats['total_files'] += 1
                if file_path.suffix == '.py':
                    self.project_stats['python_files'] += 1
                    
        self.logger.info(f"هيكل المشروع: {self.project_stats['python_files']} ملف بايثون")

    async def check_environment_variables(self):
        """فحص متغيرات البيئة"""
        env_file = self.project_path / '.env'
        required_vars = ['ACCESS_TOKEN', 'VERIFY_TOKEN', 'DATABASE_URL', 'WHATSAPP_PHONE_NUMBER_ID']
        
        if not env_file.exists():
            issue = Issue(
                id=f"env_missing_{datetime.now().timestamp()}",
                type='error',
                title='ملف .env غير موجود',
                description='ملف البيئة الأساسي مفقود',
                file_path='.env',
                solution='أنشئ ملف .env وأضف المتغيرات المطلوبة',
                confidence=1.0,
                tags=['environment', 'critical']
            )
            self.current_issues.append(issue)
            return

        try:
            content = env_file.read_text(encoding='utf-8')
            for var in required_vars:
                if var not in content:
                    issue = Issue(
                        id=f"env_var_missing_{var}",
                        type='error',
                        title=f'المتغير {var} مفقود',
                        description=f'المتغير البيئي المطلوب {var} غير موجود في .env',
                        file_path='.env',
                        solution=f'أضف {var}=قيمتك إلى ملف .env',
                        confidence=0.9,
                        tags=['environment', 'configuration']
                    )
                    self.current_issues.append(issue)
                elif f'{var}=' in content and not content.split(f'{var}=')[1].strip():
                    issue = Issue(
                        id=f"env_var_empty_{var}",
                        type='warning',
                        title=f'المتغير {var} فارغ',
                        description=f'المتغير {var} موجود لكن قيمته فارغة',
                        file_path='.env',
                        solution=f'أضف قيمة مناسبة لـ {var}',
                        confidence=0.8,
                        tags=['environment', 'configuration']
                    )
                    self.current_issues.append(issue)
        except Exception as e:
            self.logger.error(f"خطأ في قراءة ملف .env: {e}")

    async def check_dependencies(self):
        """فحص التبعيات والمكتبات"""
        for file_path in self.project_path.rglob('*.py'):
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines()
                
                for i, line in enumerate(lines, 1):
                    if line.startswith('import ') or line.startswith('from '):
                        parts = line.split()
                        if len(parts) >= 2:
                            module = parts[1].split('.')[0]
                            if module and not module.startswith('.'):
                                try:
                                    __import__(module)
                                except ImportError as e:
                                    issue = Issue(
                                        id=f"missing_dep_{module}_{datetime.now().timestamp()}",
                                        type='error',
                                        title=f'مكتبة {module} مفقودة',
                                        description=f'المكتبة المطلوبة {module} غير مثبتة',
                                        file_path=str(file_path.relative_to(self.project_path)),
                                        line_number=i,
                                        solution=f'قم بتثبيت المكتبة: pip install {module}',
                                        confidence=0.95,
                                        tags=['dependencies', 'python']
                                    )
                                    self.current_issues.append(issue)
            except Exception as e:
                self.logger.warning(f"تعذر فحص الملف {file_path}: {e}")

    async def check_supabase_connection(self):
        """فحص اتصال Supabase"""
        if not self.supabase:
            issue = Issue(
                id='supabase_not_configured',
                type='warning',
                title='Supabase غير مهيأ',
                description='اتصال Supabase غير مضبوط',
                solution='تأكد من إعداد SUPABASE_URL و SUPABASE_KEY',
                confidence=0.7,
                tags=['database', 'configuration']
            )
            self.current_issues.append(issue)
            return

        try:
            # اختبار اتصال بسيط
            result = self.supabase.table('issues').select('id').limit(1).execute()
            if hasattr(result, 'error') and result.error:
                raise Exception(result.error)
        except Exception as e:
            issue = Issue(
                id='supabase_connection_failed',
                type='error',
                title='فشل اتصال Supabase',
                description=f'تعذر الاتصال بقاعدة البيانات: {str(e)}',
                solution='تحقق من إعدادات الاتصال وشبكة الإنترنت',
                confidence=0.9,
                tags=['database', 'connection', 'critical']
            )
            self.current_issues.append(issue)

    async def analyze_code_quality(self):
        """تحليل جودة الكود الأساسي"""
        common_issues_patterns = {
            'broad-except': 'استخدام except عام بدون تحديد نوع الخطأ',
            'unused-import': 'استيراد مكتبات غير مستخدمة',
            'undefined-variable': 'استخدام متغير غير معرف',
        }
        
        for file_path in self.project_path.rglob('*.py'):
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines()
                
                # كشف الأخطاء الشائعة
                for i, line in enumerate(lines, 1):
                    if 'except:' in line or 'except Exception:' in line:
                        issue = Issue(
                            id=f"broad_except_{file_path.name}_{i}",
                            type='warning',
                            title='استثناء عام',
                            description='يستخدم استثناء عام قد يخفي أخطاء مهمة',
                            file_path=str(file_path.relative_to(self.project_path)),
                            line_number=i,
                            solution='حدد أنواع الاستثناءات المحددة بدقة',
                            confidence=0.7,
                            tags=['code-quality', 'python']
                        )
                        self.current_issues.append(issue)
                        
            except Exception as e:
                self.logger.warning(f"تعذر تحليل جودة الكود في {file_path}: {e}")

    async def apply_learning_filters(self):
        """تطبيق مرشحات التعلم لتقليل الإنذارات الكاذبة"""
        if not self.learning_engine:
            return
            
        filtered_issues = []
        for issue in self.current_issues:
            if self.learning_engine.should_alert(issue):
                filtered_issues.append(issue)
            else:
                self.project_stats['false_positives_count'] += 1
                self.logger.info(f"تم تصفية إنذار كاذب: {issue.title}")
                
        self.current_issues = filtered_issues

    async def send_scan_report(self):
        """إرسال تقرير المسح"""
        report = {
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'project_name': self.project_name,
            'stats': self.project_stats,
            'issues': [asdict(issue) for issue in self.current_issues],
            'summary': {
                'total_issues': len(self.current_issues),
                'errors': len([i for i in self.current_issues if i.type == 'error']),
                'warnings': len([i for i in self.current_issues if i.type == 'warning']),
                'critical_issues': len([i for i in self.current_issues if 'critical' in i.tags])
            }
        }
        
        # حفظ التقرير محلياً
        report_file = self.reports_dir / f'scan_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # إرسال إلى API الرئيسي إذا كان متاحاً
        await self.send_to_main_api(report)
        
        # إرسال إشعارات للمشكلات الحرجة
        await self.send_critical_notifications(report)
        
        self.logger.info(f"تم إنشاء التقرير: {report_file}")

    async def send_to_main_api(self, report: Dict):
        """إرسال التقرير إلى API الرئيسي"""
        api_endpoint = self.config.get('api_endpoint')
        if not api_endpoint:
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{api_endpoint}/events", json=report) as response:
                    if response.status == 200:
                        self.logger.info("تم إرسال التقرير إلى API الرئيسي")
                    else:
                        self.logger.warning(f"فشل إرسال التقرير إلى API: {response.status}")
        except Exception as e:
            self.logger.error(f"خطأ في إرسال التقرير إلى API: {e}")

    async def send_critical_notifications(self, report: Dict):
        """إرسال إشعارات للمشكلات الحرجة"""
        if not self.config.get('notification_enabled', True):
            return
            
        critical_issues = [issue for issue in self.current_issues if 'critical' in issue.tags]
        
        if critical_issues:
            message = f"🚨 <b>مشاكل حرجة في {self.project_name}</b>\n\n"
            for issue in critical_issues[:3]:  # أول 3 مشاكل حرجة فقط
                message += f"• {issue.title}\n"
                message += f"  الحل: {issue.solution}\n\n"
                
            message += f"إجمالي المشاكل: {len(critical_issues)}"
            
            # إرسال عبر Telegram
            await self.notification_manager.send_telegram(message)
            
            # إرسال عبر Webhook
            await self.notification_manager.send_webhook({
                'event': 'critical_issues',
                'project': self.project_name,
                'critical_count': len(critical_issues),
                'issues': [asdict(issue) for issue in critical_issues]
            })

    async def get_system_status(self) -> Dict:
        """الحصول على حالة النظام الحالية"""
        return {
            'status': 'running',
            'agent_id': self.agent_id,
            'project_name': self.project_name,
            'last_scan': self.project_stats['last_scan'],
            'active_issues': len(self.current_issues),
            'false_positives': self.project_stats['false_positives_count'],
            'next_scan_in': 'قريباً'  # يمكن حساب الوقت الفعلي
        }

    async def get_issues_summary(self) -> Dict:
        """ملخص المشاكل الحالية"""
        return {
            'total': len(self.current_issues),
            'by_type': {
                'errors': len([i for i in self.current_issues if i.type == 'error']),
                'warnings': len([i for i in self.current_issues if i.type == 'warning']),
                'info': len([i for i in self.current_issues if i.type == 'info'])
            },
            'by_severity': {
                'critical': len([i for i in self.current_issues if 'critical' in i.tags]),
                'high': len([i for i in self.current_issues if 'high' in i.tags]),
                'medium': len([i for i in self.current_issues if 'medium' in i.tags]),
                'low': len([i for i in self.current_issues if 'low' in i.tags])
            },
            'issues': [asdict(issue) for issue in self.current_issues[:10]]  # أول 10 مشاكل فقط
        }

# FastAPI Application للواجهة الرئيسية
if FastAPI is not None:
    app = FastAPI(title="Smart Project Guardian Ultra API", version="2.0.0")
    
    # إعداد CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # تخزين حالة النظام
    system_state = {}
    
    @app.on_event("startup")
    async def startup_event():
        """تهيئة النظام عند البدء"""
        # هنا يمكنك تهيئة الحارس الرئيسي
        pass
    
    @app.get("/")
    async def root():
        return {"message": "Smart Project Guardian Ultra API", "version": "2.0.0"}
    
    @app.get("/v1/status")
    async def get_status():
        """الحصول على حالة النظام"""
        return system_state.get('status', {'status': 'initializing'})
    
    @app.post("/v1/events")
    async def receive_events(event: Dict):
        """استقبال الأحداث من الوكلاء"""
        # معالجة وتخزين الأحداث
        return {"status": "received", "event_id": f"evt_{datetime.now().timestamp()}"}
    
    @app.websocket("/v1/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """اتصال WebSocket للتنبيهات الفورية"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                # معالجة البيانات الواردة
                await websocket.send_json({"status": "received", "timestamp": datetime.now().isoformat()})
        except WebSocketDisconnect:
            pass

def main():
    """الدالة الرئيسية للتشغيل"""
    parser = argparse.ArgumentParser(description='Smart Project Guardian Ultra')
    parser.add_argument('--project-path', default='/opt/ashal-bot/', help='مسار المشروع')
    parser.add_argument('--supabase-url', help='رابط Supabase')
    parser.add_argument('--supabase-key', help='مفتاح Supabase')
    parser.add_argument('--start-api', action='store_true', help='بدء واجهة API')
    parser.add_argument('--scan-now', action='store_true', help='تشغيل مسح فوري')
    
    args = parser.parse_args()
    
    # تهيئة الحارس
    guardian = SmartProjectGuardianUltra(
        project_path=args.project_path,
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key
    )
    
    if args.start_api:
        # بدء واجهة API
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif args.scan_now:
        # تشغيل مسح فوري
        asyncio.run(guardian.run_comprehensive_scan())
    else:
        # وضع الخدمة (المراقبة التلقائية)
        asyncio.run(guardian.auto_monitoring_loop())

if __name__ == "__main__":
    main()
