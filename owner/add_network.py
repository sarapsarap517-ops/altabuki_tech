import flet as ft

from services.network_manager import (
    create_network_request,
)


def add_network_view(page, current_user=None, navigate=None):
    user = current_user
    if user is None:
        user = getattr(
            page,
            "current_user",
            None,
        )

    if not isinstance(user, dict):
        page.go("/login")
        return ft.View("/owner/add-network", [])

    owner_user_id = user.get(
        "user_id"
    )

    owner_name = ft.TextField(
        label="اسم صاحب الشبكة",
        value=str(
            user.get("name", "")
        ),
        text_align=ft.TextAlign.RIGHT,
    )

    network_name = ft.TextField(
        label="اسم الشبكة",
        text_align=ft.TextAlign.RIGHT,
    )

    area = ft.TextField(
        label="المنطقة",
        text_align=ft.TextAlign.RIGHT,
    )

    phone = ft.TextField(
        label="رقم التواصل",
        keyboard_type=ft.KeyboardType.PHONE,
        text_align=ft.TextAlign.RIGHT,
    )

    message = ft.Text(
        "",
        text_align=ft.TextAlign.CENTER,
    )

    def submit(e):
        message.value = ""

        try:
            network = create_network_request(
                owner_user_id=owner_user_id,
                owner_name=(
                    owner_name.value or ""
                ).strip(),
                network_name=(
                    network_name.value or ""
                ).strip(),
                area=(
                    area.value or ""
                ).strip(),
                phone=(
                    phone.value or ""
                ).strip(),
            )

            message.value = (
                "تم إرسال طلب الشبكة بنجاح.\n"
                "الحالة: بانتظار مراجعة الإدارة."
            )

            network_name.value = ""
            area.value = ""
            phone.value = ""

            page.update()

        except ValueError as ex:
            message.value = str(ex)
            page.update()

        except Exception as ex:
            message.value = (
                f"حدث خطأ: {ex}"
            )
            page.update()

    return ft.View(
        "/owner/add-network",
        [
            ft.AppBar(
                title=ft.Text(
                    "إضافة شبكة"
                ),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: (
                        navigate("my_networks")
                        if navigate
                        else page.go("/owner/my-networks")
                    ),
                ),
            ),

            ft.Container(
                content=ft.Column(
                    [
                        owner_name,
                        network_name,
                        area,
                        phone,

                        message,

                        ft.ElevatedButton(
                            "إرسال طلب المراجعة",
                            width=300,
                            on_click=submit,
                        ),
                    ],
                    spacing=15,
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                ),
                padding=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
