import flet as ft

from services.user_manager import authenticate_user


def login_view(page, on_login=None, on_register=None):
    phone_field = ft.TextField(
        label="رقم الهاتف",
        hint_text="رقم حسابك",
        keyboard_type=ft.KeyboardType.PHONE,
        text_align=ft.TextAlign.RIGHT,
    )

    password_field = ft.TextField(
        label="كلمة المرور",
        password=True,
        can_reveal_password=True,
        text_align=ft.TextAlign.RIGHT,
    )

    message = ft.Text(
        "",
        text_align=ft.TextAlign.CENTER,
    )

    def login_click(e):
        phone = (
            phone_field.value or ""
        ).strip()

        password = (
            password_field.value or ""
        )

        message.value = ""

        try:
            user = authenticate_user(
                phone,
                password,
            )

            if not isinstance(user, dict):
                raise ValueError(
                    "تعذر تسجيل الدخول"
                )

            # هذا هو حساب المستخدم داخل التطبيق.
            # ليس رقم المستفيد الذي سيُدخل لاحقًا عند الشراء.
            page.current_user = user

            if on_login:
                on_login(user)
            else:
                page.go("/home")

        except ValueError as ex:
            message.value = str(ex)
            page.update()

        except Exception as ex:
            message.value = (
                f"حدث خطأ أثناء تسجيل الدخول: {ex}"
            )
            page.update()

    def register_click(e):
        if on_register:
            on_register()
        else:
            page.go("/register")

    return ft.View(
        "/login",
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "التبوكي باي",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Text(
                            "تسجيل الدخول",
                            size=22,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        phone_field,
                        password_field,

                        message,

                        ft.ElevatedButton(
                            "دخول",
                            width=300,
                            on_click=login_click,
                        ),

                        ft.TextButton(
                            "إنشاء حساب جديد",
                            on_click=register_click,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18,
                ),
                padding=30,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )
