import flet as ft


def account_view(
    page,
    current_user=None,
    navigate=None,
    logout=None,
):
    user = current_user

    if not isinstance(user, dict):
        return ft.Column(
            controls=[
                ft.Text("لا يوجد حساب مسجل."),
            ]
        )

    name = str(
        user.get("name", "")
        or "بدون اسم"
    )
    phone = str(
        user.get("phone", "")
        or "بدون رقم"
    )
    role = str(
        user.get("role", "")
        or "customer"
    )

    controls = [
        ft.TextButton(
            "← الرئيسية",
            on_click=lambda e: (
                navigate("home")
                if navigate
                else None
            ),
        ),
        ft.Text(
            "حسابي",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Divider(),
        ft.Text(f"الاسم: {name}"),
        ft.Text(f"رقم الهاتف: {phone}"),
        ft.Text(f"نوع الحساب: {role}"),
    ]

    if logout:
        controls.extend(
            [
                ft.Divider(),
                ft.OutlinedButton(
                    "تسجيل الخروج",
                    on_click=lambda e: logout(),
                ),
            ]
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=controls,
    )
