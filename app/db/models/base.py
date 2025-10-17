from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# نستخدم متغير البيئة لضمان الاتصال بقاعدة البيانات الخاصة بك في Supabase
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ملاحظة: يجب أن تكون هذه الجداول موجودة بالفعل في Supabase.
