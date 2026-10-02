import flet as ft

from services.report_manager import (
    get_dashboard_report,
)


def reports_view(
    page,
    current_user=None,
    navigate=None,
):
    report = get_dashboard_report()

    if not isinstance(report, dict):
        report = {}

    def value(*keys):
        for key in keys:
            if key in report:
                return report[key]
        return 0

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.TextButton(
                "← الرئيسية",
                on_click=lambda e: (
                    navigate("home")
                    if navigate
                    else None
                ),
            ),
            ft.Text(
                "التقارير",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"عدد العمليات: "
                                f"{value('transactions_count', 'total_transactions')}"
                            ),
                            ft.Text(
                                f"إجمالي المبيعات: "
                                f"{value('total_amount', 'total_sales')}"
                            ),
                            ft.Text(
                                f"إجمالي العمولات: "
                                f"{value('total_commission', 'total_commissions')}"
                            ),
                            ft.Text(
                                f"حصة أصحاب الشبكات: "
                                f"{value('total_owner_amount', 'owner_amount')}"
                            ),
                            ft.Text(
                                f"إجمالي الكمية: "
                                f"{value('total_quantity', 'total_cards')}"
                            ),
                        ]
                    ),
                )
            ),
        ],
    )
