import flet as ft


def wallet_view(
    page,
    current_user=None,
    navigate=None,
):
    user = current_user

    if not isinstance(user, dict):
        return ft.Column(
            controls=[
                ft.Text("يجب تسجيل الدخول أولًا."),
            ]
        )

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
                "المحفظة",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "الرصيد الحالي",
                                size=18,
                            ),
                            ft.Text(
                                "0 ريال",
                                size=30,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                )
            ),
            ft.Text(
                "سيتم ربط عمليات الإيداع والسحب والدفع لاحقًا.",
                size=14,
            ),
        ],
    )
