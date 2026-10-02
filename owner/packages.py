import flet as ft

from services.package_manager import (
    get_packages_for_network,
    create_package,
    deactivate_package,
)
from services.network_manager import get_network


def packages_view(
    page,
    network_id,
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
            "/owner/packages",
            [],
        )

    try:
        network_id = int(network_id)
    except (TypeError, ValueError):
        return ft.View(
            "/owner/packages",
            [
                ft.Text(
                    "رقم الشبكة غير صحيح.",
                    text_align=ft.TextAlign.CENTER,
                )
            ],
        )

    network = get_network(network_id)

    if network is None:
        return ft.View(
            "/owner/packages",
            [
                ft.Text(
                    "الشبكة غير موجودة.",
                    text_align=ft.TextAlign.CENTER,
                )
            ],
        )

    owner_user_id = user.get("user_id")

    try:
        owner_user_id = int(owner_user_id)
    except (TypeError, ValueError):
        page.go("/login")
        return ft.View(
            "/owner/packages",
            [],
        )

    if int(network.get("owner_user_id", 0)) != owner_user_id:
        return ft.View(
            "/owner/packages",
            [
                ft.AppBar(
                    title=ft.Text("باقات الشبكة"),
                ),
                ft.Container(
                    content=ft.Text(
                        "ليس لديك صلاحية إدارة هذه الشبكة.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=30,
                ),
            ],
        )

    if network.get("status") != "approved":
        return ft.View(
            "/owner/packages",
            [
                ft.AppBar(
                    title=ft.Text("باقات الشبكة"),
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
                            ft.Text(
                                "🔒 الشبكة غير معتمدة",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "يمكن إدارة الباقات بعد اعتماد الشبكة من الإدارة.",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                        spacing=12,
                    ),
                    padding=30,
                ),
            ],
        )

    network_name = network.get(
        "network_name",
        "شبكتي",
    )

    packages = get_packages_for_network(
        network_id
    )

    def refresh():
        if navigate:
            navigate(
                "packages",
                network_id=network_id,
            )
        else:
            page.go(
                f"/owner/network/{network_id}"
            )

    def add_package(e):
        name = ft.TextField(
            label="اسم الباقة",
            text_align=ft.TextAlign.RIGHT,
        )

        denomination = ft.TextField(
            label="الفئة / القيمة",
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
        )

        price = ft.TextField(
            label="السعر",
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
        )

        commission = ft.TextField(
            label="العمولة",
            value="0",
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
        )

        data_amount = ft.TextField(
            label="حجم البيانات",
            hint_text="مثال: 600 ميجا",
            text_align=ft.TextAlign.RIGHT,
        )

        validity_days = ft.TextField(
            label="مدة الصلاحية بالأيام",
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
        )

        message = ft.Text(
            "",
            text_align=ft.TextAlign.CENTER,
        )

        def close_dialog(e=None):
            dialog.open = False
            page.update()

        def save_package(e):
            message.value = ""

            try:
                package = create_package(
                    network_id=network_id,
                    denomination=denomination.value,
                    price=price.value,
                    commission=commission.value or 0,
                    name=name.value or "",
                    data_amount=data_amount.value or "",
                    validity_days=(
                        validity_days.value or 0
                    ),
                )

                dialog.open = False
                page.update()
                refresh()

            except ValueError as ex:
                message.value = str(ex)
                page.update()

            except Exception as ex:
                message.value = (
                    f"حدث خطأ: {ex}"
                )
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "➕ إضافة باقة"
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        name,
                        denomination,
                        price,
                        commission,
                        data_amount,
                        validity_days,
                        message,
                    ],
                    spacing=10,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=350,
            ),
            actions=[
                ft.TextButton(
                    "إلغاء",
                    on_click=close_dialog,
                ),
                ft.ElevatedButton(
                    "إضافة",
                    on_click=save_package,
                ),
            ],
            actions_alignment=(
                ft.MainAxisAlignment.CENTER
            ),
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def deactivate(e, package_id):
        try:
            deactivate_package(
                package_id
            )
            refresh()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"تعذر تعطيل الباقة: {ex}"
                )
            )
            page.snack_bar.open = True
            page.update()

    controls = [
        ft.Text(
            network_name,
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        ),
        ft.Text(
            "🟢 الشبكة معتمدة",
            text_align=ft.TextAlign.CENTER,
        ),
        ft.ElevatedButton(
            "➕ إضافة باقة",
            on_click=add_package,
        ),
        ft.Divider(),
    ]

    if not packages:
        controls.append(
            ft.Container(
                content=ft.Text(
                    "لا توجد باقات لهذه الشبكة حتى الآن.",
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=20,
            )
        )

    for package in packages:
        package_id = package.get(
            "package_id"
        )

        package_name = package.get(
            "name"
        ) or "باقة بدون اسم"

        denomination = package.get(
            "denomination",
            0,
        )

        price = package.get(
            "price",
            0,
        )

        commission = package.get(
            "commission",
            0,
        )

        data_amount = package.get(
            "data_amount",
            "",
        )

        validity_days = package.get(
            "validity_days",
            0,
        )

        def open_cards(
            e,
            pid=package_id,
        ):
            if navigate:
                navigate(
                    "cards",
                    package_id=pid,
                    network_id=network_id,
                )
            else:
                page.go(
                    f"/owner/cards/{pid}"
                )

        def disable_package(
            e,
            pid=package_id,
        ):
            deactivate(
                e,
                pid,
            )

        controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            package_name,
                            size=19,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"الفئة: {denomination:g}"
                            if isinstance(
                                denomination,
                                float,
                            )
                            else f"الفئة: {denomination}"
                        ),
                        ft.Text(
                            f"السعر: {price:g} ريال"
                            if isinstance(
                                price,
                                float,
                            )
                            else f"السعر: {price} ريال"
                        ),
                        ft.Text(
                            f"العمولة: {commission:g} ريال"
                            if isinstance(
                                commission,
                                float,
                            )
                            else f"العمولة: {commission} ريال"
                        ),
                        ft.Text(
                            f"البيانات: {data_amount}"
                        ),
                        ft.Text(
                            f"الصلاحية: {validity_days} يوم"
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "➕ إضافة الكروت",
                                    on_click=open_cards,
                                ),
                                ft.TextButton(
                                    "تعطيل الباقة",
                                    on_click=disable_package,
                                ),
                            ],
                            alignment=(
                                ft.MainAxisAlignment.CENTER
                            ),
                            wrap=True,
                        ),
                    ],
                    spacing=6,
                ),
                padding=15,
                border=ft.border.all(
                    1,
                    ft.colors.GREY_300,
                ),
                border_radius=10,
            )
        )

    return ft.View(
        "/owner/packages",
        [
            ft.AppBar(
                title=ft.Text(
                    "إدارة الباقات"
                ),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: (
                        navigate("my_networks")
                        if navigate
                        else page.go(
                            "/owner/my-networks"
                        )
                    ),
                ),
            ),
            ft.Container(
                content=ft.Column(
                    controls,
                    spacing=12,
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                ),
                padding=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
