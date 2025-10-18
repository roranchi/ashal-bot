from fastapi_admin.app import app as admin_app
from fastapi_admin.resources import Link
from fastapi import FastAPI
import redis.asyncio as redis

async def startup_admin(app: FastAPI):
    redis_client = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await admin_app.configure(
        redis=redis_client,
    )

    # تسجيل الروابط
    @admin_app.register
    class HomeLink(Link):
        label = "الرئيسية"
        url = "/"
        icon = "fas fa-home"

    @admin_app.register
    class ClientsLink(Link):
        label = "العملاء"
        url = "/dashboard/clients"
        icon = "fas fa-briefcase"

    @admin_app.register
    class PropertiesLink(Link):
        label = "العقارات"
        url = "/dashboard/properties"
        icon = "fas fa-building"

    @admin_app.register
    class TenantsLink(Link):
        label = "المستأجرين"
        url = "/dashboard/tenants"
        icon = "fas fa-users"

    @admin_app.register
    class ContractsLink(Link):
        label = "العقود"
        url = "/dashboard/contracts"
        icon = "fas fa-file-contract"

    @admin_app.register
    class PaymentsLink(Link):
        label = "المدفوعات"
        url = "/dashboard/payments"
        icon = "fas fa-dollar-sign"

    @admin_app.register
    class WhatsAppMessagesLink(Link):
        label = "رسائل واتساب"
        url = "/dashboard/messages"
        icon = "fab fa-whatsapp"

    @admin_app.register
    class ReportsLink(Link):
        label = "التقارير"
        url = "/dashboard/reports"
        icon = "fas fa-chart-bar"

    @admin_app.register
    class SettingsLink(Link):
        label = "الإعدادات"
        url = "/dashboard/settings"
        icon = "fas fa-cog"

    return admin_app
