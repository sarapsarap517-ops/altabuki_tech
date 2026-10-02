import flet as ft

from services.network_manager import (
    get_networks_by_owner,
)


def my_networks_view(page, current_user=None, navigate=None, logout=None):
    user = current_user
    if user is None:
        user = getattr(
            page,
            "current_user",
            None,
        )

    if not isinstance(user, dict):
        page.go("/login")
        return ft.View("/owner/my-networks", [])

    owner_user_id = user.get("user_id")

    networks = get_networks_by_owner(
        owner_user_id
    )

    controls = []

    if not networks:
        controls.append(
            ft.Text(
                "لا توجد شبكات مرتبطة بهذا الحساب.",
                text_align=ft.TextAlign.CENTER,
            )
        )

    for network in networks:
        network_id = network.get(
            "network_id"
        )

        network_name = network.get(
            "network_name",
            "بدون اسم",
        )

        area = network.get(
            "area",
            "",
        )

        status = network.get(
            "status",
            "pending",
        )

        status_text = {
            "pending": "🟡 قيد المراجعة",
            "approved": "🟢 معتمدة — يمكنك إدارة الشبكة",
            "rejected": "🔴 مرفوضة",
        }.get(
            status,
            status,
        )

        rejection_reason = network.get(
            "rejection_reason"
        )

        def open_network(
            e,
            nid=network_id,
            network_status=status,
        ):
            if network_status != "approved":
                return

            if navigate:
                navigate(
                    "packages",
                    network_id=nid,
                )
            else:
                page.go(
                    f"/owner/network/{nid}"
                )

        controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            network_name,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            f"المنطقة: {area}"
                        ),

                        ft.Text(
                            status_text
                        ),

                        ft.Text(
                            f"سبب الرفض: {rejection_reason}",
                            visible=(
                                status == "rejected"
                                and bool(rejection_reason)
                            ),
                        ),

                        ft.ElevatedButton(
                            "إدارة الشبكة"
                            if status == "approved"
                            else "قيد المراجعة"
                            if status == "pending"
                            else "الشبكة مرفوضة",
                            on_click=open_network
                            if status == "approved"
                            else None,
                            disabled=(status != "approved"),
                        ),
                    ],
                    spacing=8,
                ),
                padding=15,
                border=ft.border.all(
                    1,
                    ft.colors.GREY_300,
                ),
                border_radius=10,
            )
        )

    def add_network(e):
        if navigate:
            navigate("add_network")
        else:
            page.go(
                "/owner/add-network"
            )

    def available_networks(e):
        if navigate:
            navigate("networks")
        else:
            page.go("/available-networks")

    def network_gallery(e):
        if navigate:
            navigate("network_gallery")
        else:
            page.go("/networks")

    return ft.View(
        "/owner/my-networks",
        [
            ft.AppBar(
                title=ft.Text(
                    "شبكاتي"
                ),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: (
                        navigate("home")
                        if navigate
                        else page.go("/home")
                    ),
                ),
            ),

            ft.Container(
                content=ft.Column(
                    [
                        ft.ElevatedButton(
                            "➕ أضف شبكتك مجانًا",
                            on_click=add_network,
                        ),

                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.OutlinedButton(
                                    "الشبكات المتاحة",
                                    on_click=available_networks,
                                ),
                                ft.OutlinedButton(
                                    "معرض الشبكات",
                                    on_click=network_gallery,
                                ),
                            ],
                        ),

                        ft.Divider(),

                        *controls,
                    ],
                    spacing=15,
                ),
                padding=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
