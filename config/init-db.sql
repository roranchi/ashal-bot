-- تهيئة قاعدة البيانات للإنتاج
CREATE USER ashal_user WITH PASSWORD 'secure_password_here';
CREATE DATABASE ashal_bot_db OWNER ashal_user;
GRANT ALL PRIVILEGES ON DATABASE ashal_bot_db TO ashal_user;

-- إعدادات إضافية لتحسين الأداء
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
