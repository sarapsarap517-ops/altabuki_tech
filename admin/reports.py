import flet as ft

from services.report_manager import (
    get_dashboard_report,
)

from services.accounting_manager import (
    calculate_totals,
)


def admin_reports_view(page, admin_user_id):
    dashboard = get_dashboard_report()
    accounting = calculate_totals()

    content = ft.Column(
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def value(data, *keys, default=0):
        for key in keys:
            if isinstance(data, dict) and key in data:
                return data[key]
        return default

    transactions = value(
        dashboard,
        "total_transactions",
        "transactions",
        default=0,
    )

    sales = value(
        dashboard,
        "total_sales",
        "sales",
        default=0,
    )

    cards = value(
        dashboard,
        "total_cards",
        "cards",
        default=0,
    )

    commissions = value(
        dashboard,
        "total_commissions",
        "commissions",
        default=0,
    )

    owner_amount = value(
        dashboard,
        "total_owner_amount",
        "owner_amount",
        default=0,
    )

    accounting_sales = value(
        accounting,
        "total_sales",
        default=0,
    )

    accounting_commission = value(
        accounting,
        "total_commission",
        "total_commissions",
        default=0,
    )

    accounting_owner = value(
        accounting,
        "owner_amount",
        "total_owner_amount",
        default=0,
    )

    content.controls.extend(
        [
            ft.Text(
                "تقارير الإدارة",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Divider(),

            ft.Text(
                "ملخص العمليات",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"عدد العمليات: {transactions}"
                            ),
                            ft.Text(
                                f"إجمالي المبيعات: {sales}"
                            ),
                            ft.Text(
                                f"إجمالي الكروت: {cards}"
                            ),
                            ft.Text(
                                f"إجمالي العمولات: {commissions}"
                            ),
                            ft.Text(
                                f"حصة أصحاب الشبكات: {owner_amount}"
                            ),
                        ]
                    ),
                )
            ),

            ft.Text(
                "الدفتر المحاسبي",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"إجمالي المبيعات: {accounting_sales}"
                            ),
                            ft.Text(
                                f"إجمالي العمولات: {accounting_commission}"
                            ),
                            ft.Text(
                                f"إجمالي حصة أصحاب الشبكات: {accounting_owner}"
                            ),
                        ]
                    ),
                )
            ),

            ft.Divider(),

            ft.Text(
                "هذه البيانات مستخرجة من خدمات التقارير والمحاسبة مباشرة.",
                size=13,
            ),
        ]
    )

    return ft.Column(
        expand=True,
        controls=[content],
    )
