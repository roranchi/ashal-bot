from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey, Text, TIMESTAMP, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID # لاستخدام أنواع بيانات PostgreSQL المتقدمة
from .base import Base

# ملاحظة: بعض الأنواع مثل USER-DEFINED (payment_status, language_pref, category) 
# يجب التعامل معها كسلاسل نصية (String) في SQLAlchemy إذا لم يتم تعريفها كـ Enum في Python.

class Owner(Base):
    """جدول المالكين/المدراء (مفقود في Schema، لكن ضروري للـ properties.owner_id)"""
    # بما أن جدول properties يحتوي على owner_id، سنفترض وجود جدول owners
    __tablename__ = "owners"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, unique=True) # افتراضي
    email = Column(String) # افتراضي

class Property(Base):
    """جدول العقارات"""
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    # address في الـ Schema يقابل name/location في الموديل السابق، سنستخدم address
    address = Column(String, nullable=False) 
    # owner_id هو Foreign Key مهم
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    status = Column(String) # يطابق 'vacant'::character varying
    created_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    owner = relationship("Owner")

class Tenant(Base):
    """جدول المستأجرين"""
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True) # phone بدلاً من phone_number
    language_preference = Column(String) # يتم التعامل مع USER-DEFINED كـ String
    created_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True))

class Contract(Base):
    """جدول العقود"""
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    rent_amount = Column(Numeric, nullable=False)
    renewal_reminders = Column(JSONB)
    status = Column(String)
    created_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    property = relationship("Property")
    tenant = relationship("Tenant")

class Payment(Base):
    """جدول المدفوعات"""
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    amount = Column(Numeric, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String) # يتم التعامل مع USER-DEFINED كـ String
    created_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    contract = relationship("Contract")

class Technician(Base):
    """جدول الفنيين (جديد في الـ Schema)"""
    __tablename__ = "technicians"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    language_preference = Column(String) # يتم التعامل مع USER-DEFINED كـ String
    created_at = Column(TIMESTAMP(timezone=True))
    
class MaintenanceRequest(Base):
    """جدول طلبات الصيانة (جديد في الـ Schema)"""
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    category = Column(String, nullable=False) # يتم التعامل مع USER-DEFINED كـ String
    description = Column(Text, nullable=False)
    status = Column(String)
    response_time = Column(String) # تم تحويل Interval إلى String للتبسيط في Admin
    created_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    property = relationship("Property")
    tenant = relationship("Tenant")
    technician = relationship("Technician")

# إضافة الجداول المتبقية كـ Read-Only (لأنها لوج وتحليل)
class AIAgentLog(Base):
    __tablename__ = "ai_agent_logs"
    id = Column(Integer, primary_key=True)
    event_type = Column(String, nullable=False)
    details = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True))
    severity = Column(String)

class AggregatedMetric(Base):
    __tablename__ = "aggregated_metrics"
    id = Column(Integer, primary_key=True)
    metric_type = Column(String, nullable=False)
    period = Column(String, nullable=False)
    value = Column(Numeric, nullable=False)
    details = Column(JSONB)
    owner_id = Column(Integer) # يفترض أن هذا يربط بجدول Owners

