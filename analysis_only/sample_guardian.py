#!/usr/bin/env python3
"""
Smart Project Guardian Pro - النسخة الاحترافية المتكاملة
دمج جميع المميزات من النسخ الأربع مع تحسينات إضافية
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import re
import random
import sys
import argparse
import subprocess
from typing import Dict, List, Set, Optional, Tuple, Any
from flask import Flask, jsonify, request

class SmartProjectGuardianPro:
    def __init__(self, project_path='.'):
        self.project_path = Path(project_path)
        self.config_file = self.project_path / 'guardian_config.json'
        self.progress_file = self.project_path / 'daily_progress.json'
        self.log_file = self.project_path / 'guardian.log'
        self.reports_dir = self.project_path / 'guardian_reports'
        
        # إنشاء مجلد التقارير
        self.reports_dir.mkdir(exist_ok=True)

        # Logging setup متقدم
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        # حالة المشروع
        self.problems: List[Dict] = []
        self.warnings: List[Dict] = []
        self.suggestions: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.focus_today: str = ''
        self.energy_level: str = 'متوسط'
        self.project_name: str = 'Property Management WhatsApp Bot'

        # معلومات المشروع
        self.project_structure: Dict = {}
        self.database_analysis: Dict = {}
        self.env_status: Dict = {}
        self.requirements_analysis: Dict = {}
        self.security_issues: List[str] = []

        # إحصائيات المشروع
        self.project_stats = {
            'total_files': 0,
            'python_files': 0,
            'lines_of_code': 0,
            'last_modified': None
        }

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
                    self.target_date = config.get('target_date', '')
                    self.default_energy = config.get('default_energy', 'متوسط')
            else:
                self.setup_project()
        except Exception as e:
            self.logger.error(f'خطأ في قراءة config: {e}')
            self.setup_project()

    def setup_project(self) -> None:
        """إعداد المشروع لأول مرة"""
        config = {
            'project_name': self.project_name,
            'setup_date': datetime.now().isoformat(),
            'target_date': '',
            'project_type': 'whatsapp_bot_with_admin',
            'default_energy': 'متوسط',
            'version': '2.0.0'
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.logger.info('تم إعداد المشروع لأول مرة.')
        except Exception as e:
            self.logger.error(f'خطأ أثناء إنشاء config: {e}')

    def load_progress(self) -> None:
        """تحميل التقدم اليومي"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    if today in data:
                        self.completed_tasks = data[today].get('completed', [])
                        self.energy_level = data[today].get('energy', self.default_energy)
            except Exception as e:
                self.logger.warning(f'خطأ في قراءة daily_progress: {e}')

    def save_progress(self) -> None:
        """حفظ التقدم اليومي"""
        today = datetime.now().strftime('%Y-%m-%d')
        data = {}
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                self.logger.warning('daily_progress.json فارغ أو غير صالح، سيتم إنشاء جديد.')
        
        data[today] = {
            'completed': self.completed_tasks,
            'energy': self.energy_level,
            'focus': self.focus_today,
            'timestamp': datetime.now().isoformat(),
            'problems_count': len(self.problems),
            'warnings_count': len(self.warnings)
        }
        
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f'خطأ أثناء حفظ التقدم: {e}')

    def scan_project_structure(self) -> None:
        """مسح شامل لهيكل المشروع"""
        structure = {
            'core_files': set(),
            'flask_apps': set(),
            'database_files': set(),
            'dashboards': set(),
            'whatsapp_integration': set(),
            'tests': set(),
            'configs': set(),
            'backups_old': set(),
            'scripts': set(),
            'templates': set(),
            'static_files': set()
        }
        
        try:
            total_files = 0
            python_files = 0
            lines_of_code = 0
            last_modified = None
            
            for file_path in self.project_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    relative_path = str(file_path.relative_to(self.project_path))
                    file_name = file_path.name.lower()
                    
                    # تحديث آخر تعديل
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if last_modified is None or file_mtime > last_modified:
                        last_modified = file_mtime
                    
                    # تصنيف الملفات
                    if file_name in ['app.py', 'run.py', 'main.py', 'application.py']:
                        structure['flask_apps'].add(relative_path)
                        python_files += 1
                    elif any(folder in relative_path.lower() for folder in ['app/', 'src/', 'core/']):
                        structure['core_files'].add(relative_path)
                        if file_name.endswith('.py'):
                            python_files += 1
                    elif any(folder in relative_path.lower() for folder in ['database/', 'db/', 'models/', 'migrations/']):
                        structure['database_files'].add(relative_path)
                        if file_name.endswith('.py'):
                            python_files += 1
                    elif any(name in file_name for name in ['dashboard', 'admin', 'management']):
                        structure['dashboards'].add(relative_path)
                    elif 'whatsapp' in file_name or 'webhook' in file_name or 'bot' in file_name:
                        structure['whatsapp_integration'].add(relative_path)
                    elif file_name.startswith('test') or 'test' in relative_path.lower() or 'tests/' in relative_path.lower():
                        structure['tests'].add(relative_path)
                    elif file_name in ['.env', 'requirements.txt', 'procfile', 'runtime.txt', 'config.py', 'settings.py']:
                        structure['configs'].add(relative_path)
                    elif any(ext in file_name for ext in ['.save', '.backup', '.old', '.bak']):
                        structure['backups_old'].add(relative_path)
                    elif file_name.endswith('.sh') or file_name.endswith('.bat'):
                        structure['scripts'].add(relative_path)
                    elif file_name.endswith('.html') or file_name.endswith('.jinja') or file_name.endswith('.jinja2'):
                        structure['templates'].add(relative_path)
                    elif any(ext in file_name for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg']):
                        structure['static_files'].add(relative_path)
                    
                    # حساب عدد الأسطر لملفات Python
                    if file_name.endswith('.py'):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                lines_of_code += len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                        except:
                            pass
            
            # تحويل sets إلى lists
            for key in structure:
                structure[key] = list(structure[key])
            
            self.project_structure = structure
            self.project_stats = {
                'total_files': total_files,
                'python_files': python_files,
                'lines_of_code': lines_of_code,
                'last_modified': last_modified.isoformat() if last_modified else None
            }
            
            self.logger.info(f'تم مسح بنية المشروع: {total_files} ملف، {python_files} ملف بايثون، {lines_of_code} سطر كود')
            
        except Exception as e:
            self.logger.error(f'خطأ أثناء مسح بنية المشروع: {e}')

    def analyze_database_situation(self) -> None:
        """تحليل حالة قواعد البيانات"""
        analysis = {
            'sqlite_files': [],
            'postgres_usage': [],
            'supabase_usage': [],
            'mysql_usage': [],
            'db_conflicts': [],
            'connection_files': []
        }
        
        try:
            # البحث عن ملفات قاعدة البيانات
            for db_file in self.project_path.rglob('*.db'):
                analysis['sqlite_files'].append(str(db_file.relative_to(self.project_path)))
            
            # البحث عن ملفات اتصال وقواعد بيانات في الكود
            py_files = list(self.project_path.rglob('*.py'))
            for py_file in py_files:
                if py_file.name.startswith('guardian'):
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    file_rel_path = str(py_file.relative_to(self.project_path))
                    
                    # اكتشاف أنواع قواعد البيانات المستخدمة
                    if any(term in content.lower() for term in ['psycopg2', 'postgresql', 'postgres']):
                        analysis['postgres_usage'].append(file_rel_path)
                    
                    if any(term in content.lower() for term in ['sqlite3', 'sqlite', '.db']):
                        if file_rel_path not in analysis['sqlite_files']:
                            analysis['sqlite_files'].append(file_rel_path)
                    
                    if 'supabase' in content.lower():
                        analysis['supabase_usage'].append(file_rel_path)
                    
                    if any(term in content.lower() for term in ['mysql', 'pymysql', 'mysql.connector']):
                        analysis['mysql_usage'].append(file_rel_path)
                    
                    # اكتشاف ملفات الاتصال
                    if any(term in content.lower() for term in ['connect', 'connection', 'engine', 'session']):
                        if 'database' in file_rel_path.lower() or 'db' in file_rel_path.lower():
                            analysis['connection_files'].append(file_rel_path)
                            
                except Exception as e:
                    self.logger.warning(f'خطأ في قراءة {py_file}: {e}')
            
            # التحقق من التناقضات
            if analysis['sqlite_files'] and (analysis['postgres_usage'] or analysis['supabase_usage']):
                analysis['db_conflicts'].append('تناقض: SQLite مع PostgreSQL/Supabase')
            
            if analysis['supabase_usage'] and analysis['postgres_usage']:
                analysis['db_conflicts'].append('تناقض: Supabase مع PostgreSQL مباشر')
            
            self.database_analysis = analysis
            self.logger.info(f'تم تحليل قواعد البيانات: {len(analysis["db_conflicts"])} تناقضات')
            
        except Exception as e:
            self.logger.error(f'خطأ أثناء تحليل قواعد البيانات: {e}')

    def check_env_variables(self) -> None:
        """فحص متغيرات البيئة"""
        env_file = self.project_path / '.env'
        status = {
            'file_exists': env_file.exists(),
            'required_vars': {
                'ACCESS_TOKEN': False,
                'VERIFY_TOKEN': False,
                'DATABASE_URL': False,
                'FLASK_DEBUG': False,
                'HOST': False,
                'PORT': False,
                'WHATSAPP_PHONE_NUMBER_ID': False,
                'WHATSAPP_BUSINESS_ACCOUNT_ID': False
            },
            'empty_vars': [],
            'missing_vars': [],
            'insecure_vars': []
        }
        
        try:
            if env_file.exists():
                content = env_file.read_text(encoding='utf-8')
                
                for var in status['required_vars']:
                    pattern = rf'^{var}=([^\n]*)'
                    match = re.search(pattern, content, re.MULTILINE)
                    if match:
                        status['required_vars'][var] = True
                        value = match.group(1).strip()
                        
                        if not value:
                            status['empty_vars'].append(var)
                        elif self.is_insecure_value(var, value):
                            status['insecure_vars'].append(f'{var}={value}')
                    else:
                        status['missing_vars'].append(var)
            else:
                status['missing_vars'] = list(status['required_vars'].keys())
            
            self.env_status = status
            self.logger.info(f'تم فحص متغيرات البيئة: {len(status["missing_vars"])} مفقودة')
            
        except Exception as e:
            self.logger.error(f'خطأ أثناء فحص متغيرات البيئة: {e}')

    def is_insecure_value(self, var_name: str, value: str) -> bool:
        """فحص إذا كانت القيمة غير آمنة"""
        insecure_patterns = {
            'ACCESS_TOKEN': ['test', 'demo', '1234', 'password', 'secret'],
            'VERIFY_TOKEN': ['test', '1234', 'password'],
            'DATABASE_URL': ['sqlite:///', 'test.db', 'example.com'],
            'SECRET_KEY': ['secret', 'key', '1234', 'test']
        }
        
        if var_name in insecure_patterns:
            for pattern in insecure_patterns[var_name]:
                if pattern in value.lower():
                    return True
        
        # فحص إذا كانت القيمة قصيرة جداً
        if var_name in ['ACCESS_TOKEN', 'VERIFY_TOKEN', 'SECRET_KEY'] and len(value) < 10:
            return True
            
        return False

    def identify_problems(self) -> None:
        """تحديد المشاكل والتحذيرات"""
        self.problems = []
        self.warnings = []
        self.suggestions = []
        
        # 1. مشاكل قاعدة البيانات (حرجة)
        if self.database_analysis.get('db_conflicts'):
            for conflict in self.database_analysis['db_conflicts']:
                self.problems.append({
                    'type': 'critical',
                    'message': conflict,
                    'solution': 'توحيد استخدام نوع واحد من قواعد البيانات',
                    'priority': 1,
                    'category': 'database'
                })
        
        # 2. مشاكل ملف .env (عالية)
        if not self.env_status['file_exists']:
            self.problems.append({
                'type': 'high',
                'message': 'ملف .env غير موجود',
                'solution': 'إنشاء ملف .env وإضافة المتغيرات المطلوبة',
                'priority': 2,
                'category': 'environment'
            })
        else:
            for var in self.env_status['missing_vars']:
                self.problems.append({
                    'type': 'high',
                    'message': f'المتغير {var} مفقود في .env',
                    'solution': f'إضافة {var}=value إلى ملف .env',
                    'priority': 3,
                    'category': 'environment'
                })
            
            for var in self.env_status['empty_vars']:
                self.warnings.append({
                    'type': 'warning',
                    'message': f'المتغير {var} فارغ في .env',
                    'solution': f'تعيين قيمة مناسبة لـ {var}',
                    'priority': 4,
                    'category': 'environment'
                })
            
            for insecure in self.env_status['insecure_vars']:
                self.problems.append({
                    'type': 'high',
                    'message': f'قيمة غير آمنة: {insecure}',
                    'solution': 'تغيير القيمة إلى شيء أكثر أماناً',
                    'priority': 5,
                    'category': 'security'
                })
        
        # 3. مشاكل الهيكل (متوسطة)
        if not self.project_structure.get('tests'):
            self.warnings.append({
                'type': 'medium',
                'message': 'لا توجد اختبارات للمشروع',
                'solution': 'إنشاء مجلد tests وإضافة unit tests',
                'priority': 6,
                'category': 'structure'
            })
        
        # 4. اقتراحات للتحسين
        if self.project_stats['lines_of_code'] > 1000 and not self.project_structure.get('tests'):
            self.suggestions.append({
                'type': 'suggestion',
                'message': 'حجم المشروع كبير، يوصى بإضافة اختبارات',
                'priority': 7,
                'category': 'quality'
            })
        
        # ترتيب حسب الأولوية
        self.problems.sort(key=lambda x: x['priority'])
        self.warnings.sort(key=lambda x: x['priority'])
        self.suggestions.sort(key=lambda x: x['priority'])
        
        self.logger.info(f'تم تحديد {len(self.problems)} مشكلة، {len(self.warnings)} تحذير، {len(self.suggestions)} اقتراح')

    def set_focus_task(self) -> None:
        """تحديد المهمة المركزية لليوم"""
        energy_focus_map = {
            'منخفض': ['مراجعة الأخطاء', 'توثيق الكود', 'التخطيط', 'قراءة الوثائق'],
            'متوسط': ['إصلاح مشاكل متوسطة', 'تحسين الأداء', 'إضافة tests', 'تحسين الواجهة'],
            'عالي': ['إصلاح مشاكل حرجة', 'تطوير ميزات جديدة', 'تحسين البنية', 'تحسين الأمان']
        }
        
        if self.problems:
            # إيجاد أعلى مشكلة أولوية تناسب مستوى الطاقة
            for problem in self.problems:
                if (self.energy_level == 'عالي' and problem['type'] in ['critical', 'high']) or \
                   (self.energy_level == 'متوسط' and problem['type'] in ['high', 'medium']) or \
                   (self.energy_level == 'منخفض' and problem['type'] in ['medium', 'warning']):
                    self.focus_today = problem['solution']
                    break
            else:
                self.focus_today = 'مراجعة المشاكل البسيطة'
        else:
            # إذا لا توجد مشاكل، نختار مهمة بناءً على الطاقة
            self.focus_today = random.choice(energy_focus_map.get(self.energy_level, ['تحسين الأداء']))
        
        self.logger.info(f'تم تحديد المهمة اليومية: {self.focus_today}')

    def generate_project_overview(self) -> str:
        """توليد تقرير شامل عن المشروع"""
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        report = f"""
{'='*80}
📋 تقرير Smart Project Guardian Pro - {report_date}
{'='*80}
🏷️  اسم المشروع: {self.project_name}
⚡ مستوى الطاقة: {self.energy_level}
🎯 التركيز اليوم: {self.focus_today}

📊 إحصائيات المشروع:
• 📁 إجمالي الملفات: {self.project_stats['total_files']}
• 🐍 ملفات بايثون: {self.project_stats['python_files']}
• 📝 أسطر الكود: {self.project_stats['lines_of_code']}
• ⏰ آخر تعديل: {self.project_stats['last_modified'] or 'غير معروف'}

🏗️  هيكل المشروع:
• 🎯 تطبيقات Flask: {len(self.project_structure.get('flask_apps', []))}
• 🗄️  قواعد البيانات: {len(self.project_structure.get('database_files', []))}
• 💬 واتساب: {len(self.project_structure.get('whatsapp_integration', []))}
• 🧪 اختبارات: {len(self.project_structure.get('tests', []))}
• ⚙️  إعدادات: {len(self.project_structure.get('configs', []))}
"""

        # إضافة المشاكل إذا وجدت
        if self.problems:
            report += f"""
🔴 المشاكل الحرجة ({len(self.problems)}):
"""
            for i, problem in enumerate(self.problems, 1):
                report += f"\n{i}. 🚨 {problem['message']}\n   💡 الحل: {problem['solution']}\n"
        
        # إضافة التحذيرات
        if self.warnings:
            report += f"""
🟡 التحذيرات ({len(self.warnings)}):
"""
            for i, warning in enumerate(self.warnings, 1):
                report += f"\n{i}. ⚠️  {warning['message']}\n   💡 التوصية: {warning['solution']}\n"
        
        # إضافة الاقتراحات
        if self.suggestions:
            report += f"""
💡 اقتراحات للتحسين ({len(self.suggestions)}):
"""
            for i, suggestion in enumerate(self.suggestions, 1):
                report += f"\n{i}. 🌟 {suggestion['message']}\n"
        
        # إضافة المهام المكتملة
        report += f"""
{'='*80}
✅ المهام المكتملة اليوم: {len(self.completed_tasks)}
"""
        for task in self.completed_tasks[-5:]:  # آخر 5 مهام فقط
            if isinstance(task, dict):
                report += f"• {task.get('task', 'مهمة')} - {task.get('timestamp', '')}\n"
            else:
                report += f"• {task}\n"
        
        report += f"""
{'='*80}
✨ تذكير: أنتِ تقومين بعمل رائع! ركزي على شيء واحد فقط اليوم.
{'='*80}
"""
        return report

    def add_completed_task(self, task: str) -> None:
        """إضافة مهمة مكتملة"""
        self.completed_tasks.append({
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'energy_level': self.energy_level
        })
        self.save_progress()
        self.logger.info(f'تم إضافة مهمة مكتملة: {task}')

    def run_full_analysis(self) -> None:
        """تشغيل التحليل الكامل للمشروع"""
        print("🚀 بدء التحليل الشامل للمشروع...")
        self.logger.info("بدء التحليل الشامل للمشروع")
        
        # تنفيذ جميع خطوط التحليل
        self.scan_project_structure()
        self.analyze_database_situation()
        self.check_env_variables()
        self.identify_problems()
        self.set_focus_task()
        
        # توليد التقرير
        report = self.generate_project_overview()
        print(report)
        
        # حفظ التقرير في ملف
        report_filename = f"guardian_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        report_file = self.reports_dir / report_filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 التقرير محفوظ في: {report_file}")
        self.save_progress()
        
        # رسالة تحفيزية
        self.show_motivational_message()

    def quick_scan(self) -> bool:
        """فحص سريع للمشاكل الحرجة فقط"""
        self.logger.info("بدء الفحص السريع")
        
        self.analyze_database_situation()
        self.check_env_variables()
        self.identify_problems()
        
        critical_issues = [p for p in self.problems if p['type'] == 'critical']
        
        if critical_issues:
            print(f"🔴 تم اكتشاف {len(critical_issues)} مشكلة حرجة!")
            for issue in critical_issues:
                print(f"• {issue['message']}")
            return True
        else:
            print("✅ لا توجد مشاكل حرجة.")
            return False

    def show_motivational_message(self) -> None:
        """عرض رسالة تحفيزية"""
        messages = [
            "✨ أنتِ أقوى مما تتصورين! استمري في التقدم.",
            "🚀 كل خطوة صغيرة تقربك من الهدف الكبير.",
            "💪 التحديات تصنع الشخصيات القوية. أنتِ دليل على ذلك!",
            "🌟 لا تستمري في المقارنة مع الآخرين، ركزي على تقدمك الشخصي.",
            "🎯 النجاح ليس نهائيًا، والفشل ليس قاتلاً: الشجاعة هي المهمة.",
            "🔥 استخدمي طاقتك الذكية اليوم لتحقيق تقدم حقيقي!",
            "🌙 حتى لو كان التقدم بطيئاً، المهم أنكِ لا تتوقفين."
        ]
        
        message = random.choice(messages)
        print(f"\n💖 رسالة تحفيزية: {message}")

    def fix_issue(self, issue_type: str) -> bool:
        """محاولة إصلاح مشكلة تلقائياً"""
        try:
            if issue_type == 'env_missing':
                # إنشاء ملف .env إذا كان مفقوداً
                env_file = self.project_path / '.env'
                if not env_file.exists():
                    env_file.write_text("# ملف البيئة\nACCESS_TOKEN=your_token_here\nVERIFY_TOKEN=your_verify_token\n")
                    print("✅ تم إنشاء ملف .env بنجاح")
                    return True
                    
            elif issue_type == 'database_conflict':
                # اكتشاف وحل تناقضات قاعدة البيانات
                pass
                
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ أثناء الإصلاح التلقائي: {e}")
            return False

def setup_guardian_routes(app: Flask):
    """إضافة routes إدارة الجارديان إلى تطبيق Flask"""
    guardian = SmartProjectGuardianPro()
    
    @app.route('/guardian/health', methods=['GET'])
    def guardian_health():
        return jsonify({
            'status': 'active',
            'project': guardian.project_name,
            'energy_level': guardian.energy_level,
            'problems_count': len(guardian.problems),
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/guardian/report', methods=['GET'])
    def guardian_report():
        guardian.run_full_analysis()
        return jsonify({
            'message': 'تم إنشاء التقرير بنجاح',
            'problems': len(guardian.problems),
            'warnings': len(guardian.warnings)
        })
    
    @app.route('/guardian/scan', methods=['GET'])
    def guardian_scan():
        has_issues = guardian.quick_scan()
        return jsonify({
            'has_critical_issues': has_issues,
            'issues_count': len(guardian.problems)
        })
    
    @app.route('/guardian/complete-task', methods=['POST'])
    def guardian_complete_task():
        task = request.json.get('task', '')
        if task:
            guardian.add_completed_task(task)
            return jsonify({'message': 'تم إضافة المهمة بنجاح', 'task': task})
        return jsonify({'error': 'لم يتم تقديم مهمة'}), 400

def main():
    """الدالة الرئيسية للبرنامج"""
    parser = argparse.ArgumentParser(
        description='Smart Project Guardian Pro - النسخة الاحترافية - مراقب المشاريع الذكي',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python SmartProjectGuardianPro.py --scan        # فحص سريع
  python SmartProjectGuardianPro.py --full        # تحليل شامل
  python SmartProjectGuardianPro.py --energy عالي # تحديد الطاقة
  python SmartProjectGuardianPro.py --add-task "وصف المهمة"
        """
    )
    
    parser.add_argument('--scan', action='store_true', help='إجراء فحص سريع للمشاكل الحرجة')
    parser.add_argument('--full', action='store_true', help='إجراء تحليل شامل للمشروع')
    parser.add_argument('--report', action='store_true', help='عرض آخر تقرير')
    parser.add_argument('--energy', choices=['منخفض', 'متوسط', 'عالي'], help='تحديد مستوى الطاقة')
    parser.add_argument('--add-task', help='إضافة مهمة مكتملة')
    parser.add_argument('--fix', help='إصلاح مشكلة محددة')
    
    args = parser.parse_args()
    guardian = SmartProjectGuardianPro()
    
    if args.energy:
        guardian.energy_level = args.energy
        print(f"✅ تم تحديد مستوى الطاقة: {args.energy}")
        guardian.save_progress()
    
    if args.add_task:
        guardian.add_completed_task(args.add_task)
        print(f"✅ تم إضافة المهمة: {args.add_task}")
    
    if args.scan:
        if guardian.quick_scan():
            print("\n🔴 يوصى باستخدام --full للتفاصيل الكاملة")
            return 1
        else:
            print("\n✅ يمكنك المتابعة بأمان!")
            return 0
    
    if args.full:
        guardian.run_full_analysis()
        return 0
    
    if args.report:
        report_files = list(guardian.reports_dir.glob('guardian_report_*.md'))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            print(latest_report.read_text(encoding='utf-8'))
        else:
            print("📭 لا يوجد تقرير سابق. استخدم --full لإنشاء تقرير.")
    
    if args.fix:
        if guardian.fix_issue(args.fix):
            print(f"✅ تم إصلاح المشكلة: {args.fix}")
        else:
            print(f"❌ لم يتمكن من إصلاح: {args.fix}")
    
    if not any([args.scan, args.full, args.report, args.add_task, args.energy, args.fix]):
        parser.print_help()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
