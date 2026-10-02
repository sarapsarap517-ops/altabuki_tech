import flet as ft

from services.network_manager import (
    get_pending_networks,
    get_approved_networks,
    get_networks,
    approve_network,
    reject_network,
    reopen_network_request,
)


def _network_title(network):
    name = str(network.get("network_name", "") or "بدون اسم")
    owner = str(network.get("owner_name", "") or "بدون اسم")
    phone = str(network.get("phone", "") or "")
    return f"{name} — {owner} — {phone}"


def _network_details(network):
    area = str(network.get("area", "") or "غير محددة")
    status = str(network.get("status", "") or "")
    return f"المنطقة: {area} | الحالة: {status}"


def admin_networks_view(page, admin_user_id):
    content = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    message = ft.Text("")

    def refresh():
        content.controls.clear()

        pending = get_pending_networks()
        approved = get_approved_networks()
        all_networks = get_networks()

        content.controls.append(
            ft.Text(
                f"طلبات الشبكات بانتظار المراجعة: {len(pending)}",
                size=20,
                weight=ft.FontWeight.BOLD,
            )
        )

        if not pending:
            content.controls.append(
                ft.Text("لا توجد طلبات شبكات بانتظار المراجعة.")
            )

        for network in pending:

            def approve_click(e, network=network):
                try:
                    approve_network(
                        network.get("network_id"),
                        admin_user_id,
                    )
                    message.value = "تم اعتماد الشبكة."
                    refresh()
                except Exception as ex:
                    message.value = f"خطأ: {ex}"
                    page.update()

            def reject_click(e, network=network):
                try:
                    reject_network(
                        network.get("network_id"),
                        admin_user_id,
                        "تم رفض طلب الشبكة من الإدارة",
                    )
                    message.value = "تم رفض طلب الشبكة."
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
                                _network_title(network),
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                _network_details(network)
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
                    f"إجمالي الشبكات: {len(all_networks)}"
                ),
                ft.Text(
                    f"الشبكات المعتمدة: {len(approved)}"
                ),
            ]
        )

        page.update()

    refresh()

    return ft.Column(
        expand=True,
        controls=[
            ft.Text(
                "إدارة الشبكات",
                size=26,
                weight=ft.FontWeight.BOLD,
            ),
            message,
            ft.Divider(),
            content,
        ],
    )
