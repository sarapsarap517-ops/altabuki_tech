import flet as ft

from services.network_manager import get_network
from services.package_manager import get_packages_for_network


def network_details_view(
    page,
    network_id=None,
    current_user=None,
    navigate=None,
):
    network = get_network(network_id)

    if not isinstance(network, dict):
        return ft.Column(
            controls=[
                ft.Text(
                    "الشبكة غير موجودة.",
                    size=20,
                ),
                ft.TextButton(
                    "← العودة",
                    on_click=lambda e: (
                        navigate("networks")
                        if navigate
                        else None
                    ),
                ),
            ]
        )

    name = str(
        network.get("network_name", "")
        or "بدون اسم"
    )
    owner = str(
        network.get("owner_name", "")
        or "غير محدد"
    )
    area = str(
        network.get("area", "")
        or "غير محددة"
    )
    phone = str(
        network.get("phone", "")
        or ""
    )
    status = str(
        network.get("status", "")
        or ""
    )

    packages = get_packages_for_network(network_id)

    package_controls = []

    if not packages:
        package_controls.append(
            ft.Text(
                "لا توجد باقات متاحة لهذه الشبكة حاليًا.",
                text_align=ft.TextAlign.CENTER,
            )
        )
    else:
        for package in packages:
            package_name = str(package.get("name", "") or "باقة")
            price = package.get("price", 0)
            denomination = package.get("denomination", 0)
            data_amount = str(package.get("data_amount", "") or "")
            validity_days = package.get("validity_days", 0)

            package_controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(
                            spacing=7,
                            controls=[
                                ft.Text(
                                    package_name,
                                    size=19,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(f"القيمة: {denomination} ريال"),
                                ft.Text(f"السعر: {price} ريال"),
                                ft.Text(f"التحميل: {data_amount}"),
                                ft.Text(f"الصلاحية: {validity_days} يوم"),
                                ft.ElevatedButton(
                                    "شراء الآن",
                                    icon=ft.icons.SHOPPING_CART,
                                    on_click=lambda e, pid=package.get("package_id"), nid=network_id: (navigate("purchase", network_id=nid, package_id=pid) if navigate else None),
                                ),
                            ],
                        ),
                    )
                )
            )

    return ft.View(
        "/network-details",
        [
            ft.AppBar(
                title=ft.Text("تفاصيل الشبكة"),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: (
                        navigate("networks")
                        if navigate
                        else None
                    ),
                ),
            ),
            ft.Container(
                padding=20,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                    controls=[
                        ft.Text(
                            name,
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(f"صاحب الشبكة: {owner}"),
                        ft.Text(f"المنطقة: {area}"),
                        ft.Text(f"الهاتف: {phone}"),
                        ft.Text(f"الحالة: {status}"),
                        ft.Divider(),
                        ft.Text(
                            "الباقات المتاحة",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                        *package_controls,
                    ],
                ),
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
