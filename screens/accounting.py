import flet as ft

from services.accounting_manager import (
    get_user_accounting_summary,
)


def accounting_view(
    page,
    current_user=None,
    navigate=None,
):
    user_id = None

    if isinstance(current_user, dict):
        user_id = current_user.get("user_id")

    summary = {}

    if user_id is not None:
        try:
            result = get_user_accounting_summary(
                user_id
            )
            if isinstance(result, dict):
                summary = result
        except Exception:
            summary = {}

    def value(*keys):
        for key in keys:
            if key in summary:
                return summary[key]
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
                "الحسابات",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Divider(),
            ft.Text(
                f"إجمالي المبيعات: "
                f"{value('total_sales')}"
            ),
            ft.Text(
                f"إجمالي العمولات: "
                f"{value('total_commission', 'total_commissions')}"
            ),
            ft.Text(
                f"حصة صاحب الشبكة: "
                f"{value('total_owner', 'owner_amount', 'total_owner_amount')}"
            ),
            ft.Text(
                f"إجمالي الكمية: "
                f"{value('total_quantity')}"
            ),
        ],
    )
