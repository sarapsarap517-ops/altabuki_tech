import flet as ft

from services.card_manager import (
    get_cards_for_package,
)


def cards_view(
    page,
    package_id,
    network_id=None,
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
            "/owner/cards",
            [],
        )

    cards = get_cards_for_package(
        package_id
    )

    available = [
        card
        for card in cards
        if card.get(
            "status",
            "available",
        ) == "available"
    ]

    sold = [
        card
        for card in cards
        if card.get(
            "status"
        ) == "sold"
    ]

    controls = [
        ft.Text(
            f"الإجمالي: {len(cards)}"
        ),
        ft.Text(
            f"🟢 المتاح: {len(available)}"
        ),
        ft.Text(
            f"🔴 المباع: {len(sold)}"
        ),
        ft.Divider(),
    ]

    for index, card in enumerate(
        cards,
        1,
    ):
        code = card.get(
            "code",
            "",
        )

        status = card.get(
            "status",
            "available",
        )

        status_text = (
            "🟢 متاح"
            if status == "available"
            else "🔴 مباع"
        )

        controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            f"{index}- {code}",
                            expand=True,
                            text_align=(
                                ft.TextAlign.RIGHT
                            ),
                        ),
                        ft.Text(
                            status_text
                        ),
                    ],
                    alignment=(
                        ft.MainAxisAlignment
                        .SPACE_BETWEEN
                    ),
                ),
                padding=8,
                border=ft.border.all(
                    1,
                    ft.colors.GREY_300,
                ),
                border_radius=8,
            )
        )

    return ft.View(
        "/owner/cards",
        [
            ft.AppBar(
                title=ft.Text(
                    "كروت الباقة"
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
                    controls,
                    spacing=8,
                ),
                padding=15,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
