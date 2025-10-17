#!/usr/bin/env python3
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ScanResult:
    issue_id: str
    type: str
    title: str
    description: str
    file_path: Optional[str]
    confidence: float
    solution: str
    tags: List[str]

class CoreScanner:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.logger = logging.getLogger(__name__)
    
    async def scan_environment(self) -> List[ScanResult]:
        """فحص متغيرات البيئة"""
        results = []
        env_file = self.project_path / '.env'
        
        if not env_file.exists():
            results.append(ScanResult(
                issue_id="env_missing",
                type="error",
                title="ملف .env غير موجود",
                description="الملف الأساسي للبيئة مفقود",
                file_path=".env",
                confidence=1.0,
                solution="أنشئ ملف .env وأضف المتغيرات المطلوبة",
                tags=["environment", "critical"]
            ))
            return results
        
        # فحص المتغيرات المطلوبة
        required_vars = ['DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_KEY']
        try:
            content = env_file.read_text()
            
            for var in required_vars:
                if var not in content:
                    results.append(ScanResult(
                        issue_id=f"env_{var}_missing",
                        type="error", 
                        title=f"المتغير {var} مفقود",
                        description=f"المتغير البيئي المطلوب غير موجود",
                        file_path=".env",
                        confidence=0.9,
                        solution=f"أضف {var}=قيمتك إلى ملف .env",
                        tags=["environment", "configuration"]
                    ))
        except Exception as e:
            self.logger.error(f"خطأ في قراءة ملف .env: {e}")
        
        return results

    async def run_scan(self) -> List[ScanResult]:
        """تشغيل فحص شامل"""
        all_results = []
        
        # فحص البيئة
        env_results = await self.scan_environment()
        all_results.extend(env_results)
        
        return all_results
