#!/usr/bin/env python3
"""
Smart Project Guardian Pro - أداة مخصصة لمشروع Ashal Bot
تساعدك على التركيز، اكتشاف المشاكل بسرعة، وتجنب التشتت
"""

import os
import json
import logging
import random
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from supabase import Client
except ImportError:
    Client = None

class SmartProjectGuardianPro:
    def __init__(self, project_path: str = '/opt/ashal-bot/', supabase: Optional[Client] = None):
        self.project_path = Path(project_path)
        self.reports_dir = self.project_path / 'guardian_reports'
        self.config_file = self.project_path / 'guardian_config.json'
        self.progress_file = self.project_path / 'daily_progress.json'
        self.log_file = self.project_path / 'guardian.log'
        self.supabase = supabase

        # إنشاء مجلد التقارير
        self.reports_dir.mkdir(exist_ok=True)

        # إعداد اللوغ
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        # حالة المشروع
        self.project_name = 'Ashal WhatsApp Bot'
        self.energy_level = 'متوسط'
        self.problems = []
        self.warnings = []
        self.completed_tasks = []
        self.focus_task = ''
        self.project_stats = {'total_files': 0, 'python_files': 0}

        # تحميل الإعدادات والتقدم
        self.load_config()
        self.load_progress()

    def load_config(self) -> None:
        """تحميل إعدادات المشروع"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.project_name = config.get('project_name', self.project_name)
                    self.energy_level = config.get('default_energy', 'متوسط')
            else:
                self.setup_config()
        except Exception as e:
            self.logger.error(f'خطأ في تحميل الإعدادات: {e}')
            self.setup_config()

    def setup_config(self) -> None:
        """إعداد ملف الإعدادات لأول مرة"""
        config = {
            'project_name': self.project_name,
            'setup_date': datetime.now().isoformat(),
            'default_energy': 'متوسط',
            'version': '1.0.0'
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.logger.info('تم إنشاء ملف الإعدادات.')

    def load_progress(self) -> None:
        """تحميل التقدم اليومي"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    if today in data:
                        self.completed_tasks = data[today].get('completed', [])
                        self.energy_level = data[today].get('energy', 'متوسط')
                        self.focus_task = data[today].get('focus', '')
            except Exception as e:
                self.logger.warning(f'خطأ في تحميل التقدم: {e}')

    def save_progress(self) -> None:
        """حفظ التقدم اليومي"""
        today = datetime.now().strftime('%Y-%m-%d')
        data = {}
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                self.logger.warning('ملف daily_progress.json فارغ، سيتم إنشاء جديد.')

        data[today] = {
            'completed': self.completed_tasks,
            'energy': self.energy_level,
            'focus': self.focus_task,
            'timestamp': datetime.now().isoformat(),
            'problems_count': len(self.problems),
            'warnings_count': len(self.warnings)
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def scan_project(self) -> None:
        """فحص هيكل المشروع"""
        self.project_stats = {'total_files': 0, 'python_files': 0}
        for file_path in self.project_path.rglob('*.py'):
            self.project_stats['python_files'] += 1
            self.project_stats['total_files'] += 1
        self.logger.info(f'فحص المشروع: {self.project_stats["python_files"]} ملف بايثون')

    def check_env(self) -> None:
        """فحص متغيرات البيئة"""
        env_file = self.project_path / '.env'
        required_vars = ['ACCESS_TOKEN', 'VERIFY_TOKEN', 'DATABASE_URL', 'WHATSAPP_PHONE_NUMBER_ID']
        self.problems = []
        self.warnings = []

        if not env_file.exists():
            self.problems.append({
                'message': 'يا بطلة، ملف .env غير موجود!',
                'solution': 'أنشئي ملف .env في /opt/ashal-bot/ وأضيفي المتغيرات المطلوبة.'
            })
            return

        content = env_file.read_text(encoding='utf-8')
        for var in required_vars:
            if var not in content:
                self.problems.append({
                    'message': f'المتغير {var} مفقود في .env',
                    'solution': f'أضيفي {var}=قيمة في ملف .env'
                })
            elif f'{var}=' in content and not content.split(f'{var}=')[1].strip():
                self.warnings.append({
                    'message': f'المتغير {var} فارغ في .env',
                    'solution': f'أضيفي قيمة لـ {var} في ملف .env'
                })

    def check_supabase(self) -> None:
        """فحص اتصال Supabase"""
        if not self.supabase:
            self.warnings.append({
                'message': 'لم يتم تهيئة اتصال Supabase',
                'solution': 'تأكدي من تمرير عميل Supabase أو إعداد SUPABASE_URL و SUPABASE_KEY في .env'
            })
            return

        try:
            # فحص بسيط للاتصال
            result = self.supabase.table('test').select('*').limit(1).execute()
            if not result.data:
                self.warnings.append({
                    'message': 'اتصال Supabase يعمل، لكن لا توجد بيانات في جدول test',
                    'solution': 'تأكدي من إعداد الجداول في Supabase'
                })
        except Exception as e:
            self.problems.append({
                'message': f'مشكلة في اتصال Supabase: {str(e)}',
                'solution': 'تأكدي من إعداد DATABASE_URL في .env'
            })

    def check_python_files(self) -> None:
        """فحص ملفات بايثون لأخطاء شائعة"""
        for file_path in self.project_path.rglob('*.py'):
            try:
                content = file_path.read_text(encoding='utf-8')
                # فحص استيراد مكتبات مفقودة
                if 'import ' in content:
                    for line in content.splitlines():
                        if line.startswith('import ') or line.startswith('from '):
                            module = line.split()[1].split('.')[0]
                            try:
                                __import__(module)
                            except ImportError:
                                self.problems.append({
                                    'message': f'مكتبة {module} مفقودة في {file_path.name}',
                                    'solution': f'ثبتي المكتبة بـ: pip install {module}'
                                })
            except Exception as e:
                self.warnings.append({
                    'message': f'خطأ في قراءة {file_path.name}: {str(e)}',
                    'solution': 'تأكدي من صلاحيات الملف أو تنسيقه'
                })

    def set_daily_focus(self) -> None:
        """تحديد مهمة يومية واحدة بناءً على الطاقة"""
        energy_tasks = {
            'منخفض': ['مراجعة ملف .env', 'قراءة رسائل الخطأ', 'توثيق جزء صغير'],
            'متوسط': ['إصلاح متغير مفقود', 'تثبيت مكتبة مفقودة', 'اختبار واجهة واتساب'],
            'عالي': ['إصلاح مشكلة Supabase', 'إضافة ميزة جديدة', 'تحسين كود']
        }
        if self.problems:
            self.focus_task = self.problems[0]['solution']
        else:
            self.focus_task = random.choice(energy_tasks.get(self.energy_level, ['راجعي الكود']))
        self.logger.info(f'المهمة اليومية: {self.focus_task}')

    def save_report(self) -> str:
        """حفظ تقرير بسيط"""
        report = {
            'project_name': self.project_name,
            'timestamp': datetime.now().isoformat(),
            'stats': self.project_stats,
            'problems': self.problems,
            'warnings': self.warnings,
            'focus_task': self.focus_task
        }
        report_file = self.reports_dir / f'guardian_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        self.logger.info(f'تم حفظ التقرير في {report_file}')
        return str(report_file)

    def generate_summary(self) -> str:
        """توليد تقرير بسيط وسهل"""
        summary = f"""
🌟 تقرير {self.project_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}
⚡ طاقتك اليوم: {self.energy_level}
🎯 المهمة اليومية: {self.focus_task}

📊 حالة المشروع:
- 📁 عدد ملفات بايثون: {self.project_stats['python_files']}

"""
        if self.problems:
            summary += f"🔴 مشاكل تحتاجين تركزين عليها ({len(self.problems)}):\n"
            for i, problem in enumerate(self.problems, 1):
                summary += f"{i}. {problem['message']} 💡 جربي: {problem['solution']}\n"
        else:
            summary += "✅ ما فيه مشاكل كبيرة، أنتِ قوية!\n"

        if self.warnings:
            summary += f"\n🟡 تنبيهات بسيطة ({len(self.warnings)}):\n"
            for i, warning in enumerate(self.warnings, 1):
                summary += f"{i}. {warning['message']} 💡 جربي: {warning['solution']}\n"

        summary += f"\n💖 رسالة لكِ: {self.get_motivational_message()}"
        return summary

    def get_motivational_message(self) -> str:
        """رسالة تحفيزية مخصصة"""
        messages = [
            "يا بطلة، أنتِ تقدمين خطوة خطوة! خذي نفس عميق وكملي.",
            "أنتِ مذهلة! حتى لو اليوم صعب، خطوة صغيرة تكفي.",
            "ما شاء الله، تركيزك يجنن! ركزي على مهمتك اليومية بس.",
            "كل مشكلة تحلينها تقربك من هدفك، استمري يا نجمة!",
            "إذا حسيتِ بالتشتت، خذي استراحة 5 دقايق، أنتِ قدها!"
        ]
        return random.choice(messages)

    def run_full_analysis(self) -> Dict:
        """تشغيل تحليل كامل"""
        self.logger.info('🚀 بدء التحليل الكامل...')
        self.scan_project()
        self.check_env()
        self.check_supabase()
        self.check_python_files()
        self.set_daily_focus()
        report_file = self.save_report()
        print(self.generate_summary())
        print(f"💾 التقرير محفوظ في: {report_file}")
        self.save_progress()
        return {'problems': self.problems, 'warnings': self.warnings}

    def quick_scan(self) -> bool:
        """فحص سريع للمشاكل الحرجة"""
        self.logger.info('🔍 بدء فحص سريع...')
        self.check_env()
        self.check_supabase()
        critical_issues = [p for p in self.problems if 'ملف .env غير موجود' in p['message']]
        if critical_issues:
            print(f"🔴 مشكلة كبيرة: {critical_issues[0]['message']}\n💡 جربي: {critical_issues[0]['solution']}")
            return True
        print("✅ ما فيه مشاكل كبيرة، كملي شغلك يا نجمة!")
        return False

    def add_completed_task(self, task: str) -> None:
        """إضافة مهمة مكتملة"""
        self.completed_tasks.append({
            'task': task,
            'timestamp': datetime.now().isoformat()
        })
        self.save_progress()
        print(f"🎉 مبروك! خلّصتِ: {task}\n💖 خذي استراحة صغيرة وكملي!")
        self.logger.info(f'تم إضافة مهمة: {task}')

def main():
    parser = argparse.ArgumentParser(description='Smart Project Guardian Pro - أداة لتركيزك ونجاحك!')
    parser.add_argument('--scan', action='store_true', help='فحص سريع للمشاكل الكبيرة')
    parser.add_argument('--full', action='store_true', help='تحليل كامل للمشروع')
    parser.add_argument('--add-task', help='إضافة مهمة مكتملة')
    parser.add_argument('--energy', choices=['منخفض', 'متوسط', 'عالي'], help='حددي طاقتك اليوم')
    args = parser.parse_args()

    # إعداد Supabase (افتراضي، يمكن تعديله)
    supabase = None
    if 'SUPABASE_URL' in os.environ and 'SUPABASE_KEY' in os.environ:
        from supabase import create_client
        supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

    guardian = SmartProjectGuardianPro(project_path='/opt/ashal-bot/', supabase=supabase)

    if args.energy:
        guardian.energy_level = args.energy
        guardian.save_progress()
        print(f"⚡ طاقتك اليوم: {args.energy}")

    if args.add_task:
        guardian.add_completed_task(args.add_task)

    if args.scan:
        guardian.quick_scan()

    if args.full:
        result = guardian.run_full_analysis()
        print(f"✅ التحليل خلّص! المشاكل: {len(result['problems'])}, التنبيهات: {len(result['warnings'])}")

    if not any([args.scan, args.full, args.add_task, args.energy]):
        parser.print_help()

if __name__ == '__main__':
    sys.exit(main())
