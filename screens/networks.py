import flet as ft


def networks_view(
    page,
    current_user=None,
    navigate=None,
):
    user = current_user

    if user is None:
        user = getattr(
            page,
            "current_user",
            None,
        )

    if not isinstance(user, dict):
        page.go("/login")
        return ft.View(
            "/networks",
            [],
        )

    name = str(
        user.get("name", "")
        or "المستخدم"
    ).strip()

    role = str(
        user.get("role", "customer")
        or "customer"
    ).strip()

    def go_home(e=None):
        if navigate:
            navigate("home")
        else:
            page.go("/home")

    def go_my_networks(e=None):
        if navigate:
            navigate("my_networks")
        else:
            page.go("/owner/my-networks")

    def go_add_network(e=None):
        if navigate:
            navigate("add_network")
        else:
            page.go("/owner/add-network")

    add_network_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "🏪",
                        size=40,
                    ),
                    ft.Text(
                        "أضف شبكتك مجانًا",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "أضف شبكتك إلى منصة التبوكي باي "
                        "وأرسل طلبك للمراجعة.",
                        size=15,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "أضف شبكتك مجانًا",
                        width=280,
                        on_click=go_add_network,
                    ),
                ],
            ),
        ),
    )

    my_networks_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "🌐",
                        size=40,
                    ),
                    ft.Text(
                        "شبكاتي",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "إدارة شبكاتك ومتابعة حالة طلباتك.",
                        size=15,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "عرض شبكاتي",
                        width=280,
                        on_click=go_my_networks,
                    ),
                ],
            ),
        ),
    )

    info = ft.Container(
        padding=15,
        content=ft.Text(
            "ملاحظة: الشبكات المتاحة للشراء لها شاشة مستقلة "
            "ولا تظهر داخل معرض الشبكات.",
            size=14,
            text_align=ft.TextAlign.CENTER,
        ),
    )

    return ft.View(
        "/networks",
        [
            ft.AppBar(
                title=ft.Text(
                    "معرض الشبكات"
                ),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=go_home,
                ),
            ),

            ft.Container(
                padding=20,
                content=ft.Column(
                    spacing=18,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text(
                            f"مرحبًا {name}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Text(
                            "معرض الشبكات",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Text(
                            "من هنا يمكنك إضافة شبكتك "
                            "أو إدارة الشبكات الخاصة بك.",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Divider(),

                        add_network_card,

                        my_networks_card,

                        info,

                        ft.Divider(),

                        ft.TextButton(
                            "← العودة إلى الرئيسية",
                            on_click=go_home,
                        ),
                    ],
                ),
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
