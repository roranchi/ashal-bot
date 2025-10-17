from fastapi_admin.app import FastAPIAdmin
from fastapi_admin.resources import Link, Model
from fastapi_admin.providers.menus import MenuProvider
from app.db.models.models import (
    Owner, Property, Tenant, Contract, Payment, Technician, 
    MaintenanceRequest, AIAgentLog, AggregatedMetric
)
from fastapi_admin.enums import Language

class CustomMenuProvider(MenuProvider):
    def __init__(self, request):
        super().__init__(request)
        self.menus = [
            Link(
                title="الرئيسية",
                icon="fas fa-home",
                path="/admin",
                i18n={"en-US": "Home"}
            ),
            Link(
                title="إدارة العملاء والممتلكات",
                icon="fas fa-city",
                i18n={"en-US": "Client & Property Management"},
                details=[
                    Model(
                        label="المالكين/المدراء (عملائي)",
                        icon="fas fa-handshake",
                        model=Owner,
                        i18n={"en-US": "Owners/Managers"}
                    ),
                    Model(
                        label="العقارات",
                        icon="fas fa-building",
                        model=Property,
                        i18n={"en-US": "Properties"}
                    )
                ]
            ),
            Link(
                title="الإدارة المالية والعقود",
                icon="fas fa-dollar-sign",
                i18n={"en-US": "Financial & Contracts"},
                details=[
                    Model(
                        label="المستأجرين",
                        icon="fas fa-users",
                        model=Tenant,
                        i18n={"en-US": "Tenants"}
                    ),
                    Model(
                        label="العقود",
                        icon="fas fa-file-contract",
                        model=Contract,
                        i18n={"en-US": "Contracts"}
                    ),
                    Model(
                        label="المدفوعات",
                        icon="fas fa-money-check-alt",
                        model=Payment,
                        i18n={"en-US": "Payments"}
                    )
                ]
            ),
            Link(
                title="الصيانة والتشغيل",
                icon="fas fa-wrench",
                i18n={"en-US": "Maintenance & Operations"},
                details=[
                    Model(
                        label="طلبات الصيانة",
                        icon="fas fa-tools",
                        model=MaintenanceRequest,
                        i18n={"en-US": "Maintenance Requests"}
                    ),
                    Model(
                        label="الفنيون",
                        icon="fas fa-hard-hat",
                        model=Technician,
                        i18n={"en-US": "Technicians"}
                    )
                ]
            ),
            Link(
                title="سجلات وتحليلات",
                icon="fas fa-chart-line",
                i18n={"en-US": "Logs & Analytics"},
                details=[
                    Model(
                        label="مقاييس مجمعة",
                        icon="fas fa-tachometer-alt",
                        model=AggregatedMetric,
                        i18n={"en-US": "Aggregated Metrics"}
                    ),
                    Model(
                        label="سجلات الذكاء الاصطناعي",
                        icon="fas fa-robot",
                        model=AIAgentLog,
                        i18n={"en-US": "AI Agent Logs"}
                    )
                ]
            ),
            Link(
                title="API Docs",
                icon="fas fa-book",
                path="/docs",
                i18n={"en-US": "API Docs"}
            )
        ]

    async def provide_menus(self, request):
        return self.menus

async def startup_admin():
    await FastAPIAdmin.init(
        title="Ashal Bot - الإدارة الكلية",
        admin_model=None,
        session_maker=None,
        menu_provider=CustomMenuProvider,
        language="ar-SA",
        locales=[Language.ar_SA, Language.en_US],
        theme_switcher=True,
    )
