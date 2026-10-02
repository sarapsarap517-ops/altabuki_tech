from datetime import datetime
import re

from services.storage import load_json, save_json
from services.package_manager import get_package


DATA_FILE = "cards"


def _now():
    return datetime.now().isoformat()


def _load():
    data = load_json(DATA_FILE)

    if "cards" not in data:
        data["cards"] = []

    return data


def _save(data):
    save_json(DATA_FILE, data)


def _next_card_id(data):
    ids = []

    for card in data["cards"]:
        try:
            ids.append(int(card.get("card_id", 0)))
        except (TypeError, ValueError):
            pass

    return max(ids, default=0) + 1


def get_card(card_id):
    card_id = int(card_id)

    for card in _load()["cards"]:
        if int(card.get("card_id", 0)) == card_id:
            return card

    return None


def extract_card_codes(text):
    """
    يقبل الأكواد الرقمية مهما كان عدد أرقامها،
    بشرط أن تكون أرقامًا منفصلة وليست جزءًا من رقم أطول.
    """

    text = str(text or "")

    codes = re.findall(
        r"(?<!\d)\d+(?!\d)",
        text,
    )

    result = []
    seen = set()

    for code in codes:
        code = code.strip()

        if code and code not in seen:
            seen.add(code)
            result.append(code)

    return result


def add_card(package_id, code):
    package_id = int(package_id)
    code = str(code).strip()

    if get_package(package_id) is None:
        raise ValueError("الباقة غير موجودة")

    if not code:
        raise ValueError("كود الكرت فارغ")

    data = _load()

    for card in data["cards"]:
        if str(card.get("code", "")).strip() == code:
            raise ValueError("كود الكرت موجود مسبقًا")

    card = {
        "card_id": _next_card_id(data),
        "package_id": package_id,
        "code": code,
        "status": "available",
        "sold_at": None,
        "customer_phone": None,
        "created_at": _now(),
    }

    data["cards"].append(card)

    _save(data)

    return card


def add_cards(package_id, codes):
    added = []
    duplicates = []

    for code in codes:
        code = str(code).strip()

        if not code:
            continue

        try:
            added.append(
                add_card(package_id, code)
            )
        except ValueError:
            duplicates.append(code)

    return {
        "added": added,
        "duplicates": duplicates,
        "added_count": len(added),
        "duplicate_count": len(duplicates),
    }


def add_cards_from_text(package_id, text):
    codes = extract_card_codes(text)

    result = add_cards(
        package_id,
        codes,
    )

    result["found"] = codes
    result["found_count"] = len(codes)

    return result


def get_cards_for_package(package_id):
    package_id = int(package_id)

    return [
        card
        for card in _load()["cards"]
        if int(card.get("package_id", 0)) == package_id
    ]


def get_available_cards(package_id):
    return [
        card
        for card in get_cards_for_package(package_id)
        if card.get("status") == "available"
    ]


def get_sold_cards(package_id):
    return [
        card
        for card in get_cards_for_package(package_id)
        if card.get("status") == "sold"
    ]


def sell_cards(
    package_id,
    quantity,
    customer_phone=None,
):
    package_id = int(package_id)
    quantity = int(quantity)

    if quantity <= 0:
        raise ValueError("عدد الكروت يجب أن يكون أكبر من صفر")

    available = get_available_cards(package_id)

    if len(available) < quantity:
        raise ValueError(
            f"الكروت المتاحة غير كافية. "
            f"المتاح: {len(available)}"
        )

    data = _load()

    selected_ids = {
        int(card["card_id"])
        for card in available[:quantity]
    }

    now = _now()
    sold = []

    for card in data["cards"]:
        if int(card.get("card_id", 0)) in selected_ids:
            card["status"] = "sold"
            card["sold_at"] = now
            card["customer_phone"] = (
                str(customer_phone).strip()
                if customer_phone
                else None
            )
            sold.append(card.copy())

    _save(data)

    return sold


def count_available_cards(package_id):
    return len(get_available_cards(package_id))
