import flet as ft

from services.user_manager import (
    get_users_by_status,
    approve_user,
    reject_user,
    suspend_user,
)


def _user_title(user):
    name = str(user.get("name", "") or "بدون اسم")
    phone = str(user.get("phone", "") or "بدون رقم")
    role = str(user.get("role", "") or "")
    return f"{name} — {phone} — {role}"


def _user_details(user):
    status = str(user.get("status", "") or "")
    created = str(user.get("created_at", "") or "")
    return f"الحالة: {status} | تاريخ التسجيل: {created}"


def admin_users_view(page, admin_user_id):
    content = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    message = ft.Text("")


    def refresh():
        content.controls.clear()

        pending = get_users_by_status("pending")
        approved = get_users_by_status("approved")
        rejected = get_users_by_status("rejected")
        suspended = get_users_by_status("suspended")

        content.controls.append(
            ft.Text(
                f"طلبات المراجعة: {len(pending)}",
                size=20,
                weight=ft.FontWeight.BOLD,
            )
        )

        if not pending:
            content.controls.append(
                ft.Text("لا توجد حسابات بانتظار المراجعة.")
            )

        for user in pending:

            def approve_click(e, user=user):
                try:
                    approve_user(
                        user.get("user_id"),
                        admin_user_id,
                    )
                    message.value = "تم اعتماد الحساب."
                    refresh()
                except Exception as ex:
                    message.value = f"خطأ: {ex}"

                page.update()


            def reject_click(e, user=user):
                try:
                    reject_user(
                        user.get("user_id"),
                        admin_user_id,
                        "تم رفض الطلب من الإدارة",
                    )
                    message.value = "تم رفض الحساب."
                    refresh()
                except Exception as ex:
                    message.value = f"خطأ: {ex}"

                page.update()


            card = ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                _user_title(user),
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                _user_details(user)
                            ),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "اعتماد",
                                        on_click=approve_click,
                                    ),
                                    ft.OutlinedButton(
                                        "رفض",
                                        on_click=reject_click,
                                    ),
                                ]
                            ),
                        ],
                    ),
                )
            )

            content.controls.append(card)


        content.controls.extend(
            [
                ft.Divider(),
                ft.Text(
                    f"المعتمدون: {len(approved)}"
                ),
                ft.Text(
                    f"المرفوضون: {len(rejected)}"
                ),
                ft.Text(
                    f"الموقوفون: {len(suspended)}"
                ),
            ]
        )

        page.update()


    refresh()

    return ft.Column(
        expand=True,
        controls=[
            ft.Text(
                "إدارة المستخدمين",
                size=26,
                weight=ft.FontWeight.BOLD,
            ),
            message,
            ft.Divider(),
            content,
        ],
    )
