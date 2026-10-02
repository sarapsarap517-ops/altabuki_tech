import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


DATA_FILES = {
    "users": DATA_DIR / "users.json",
    "wallets": DATA_DIR / "wallets.json",
    "networks": DATA_DIR / "networks.json",
    "packages": DATA_DIR / "packages.json",
    "cards": DATA_DIR / "cards.json",
    "transactions": DATA_DIR / "transactions.json",
    "accounting": DATA_DIR / "accounting.json",
}


DEFAULT_DATA = {
    "users": {
        "users": [],
        "next_user_id": 1,
    },
    "wallets": {
        "wallets": [],
    },
    "networks": {
        "networks": [],
        "next_network_id": 1,
    },
    "packages": {
        "packages": [],
        "next_package_id": 1,
    },
    "cards": {
        "cards": [],
        "next_card_id": 1,
    },
    "transactions": {
        "transactions": [],
        "next_transaction_id": 1,
    },
    "accounting": {
        "entries": [],
        "next_entry_id": 1,
    },
}


def ensure_data_directory():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _default_copy(name: str) -> dict:
    return json.loads(
        json.dumps(
            DEFAULT_DATA[name],
            ensure_ascii=False,
        )
    )


def load_json(name: str) -> dict:
    ensure_data_directory()

    if name not in DATA_FILES:
        raise ValueError(
            f"ملف بيانات غير معروف: {name}"
        )

    path = DATA_FILES[name]

    if not path.exists():
        data = _default_copy(name)
        save_json(name, data)
        return data

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(
            f"تعذر قراءة ملف البيانات: {name}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"صيغة ملف البيانات غير صحيحة: {name}"
        )

    return data


def save_json(
    name: str,
    data: dict,
):
    ensure_data_directory()

    if name not in DATA_FILES:
        raise ValueError(
            f"ملف بيانات غير معروف: {name}"
        )

    if not isinstance(data, dict):
        raise TypeError(
            "بيانات JSON يجب أن تكون من نوع dict"
        )

    path = DATA_FILES[name]
    temp_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    try:
        with temp_path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )
            f.flush()

        temp_path.replace(path)

    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(
                missing_ok=True
            )

        raise RuntimeError(
            f"تعذر حفظ ملف البيانات: {name}"
        ) from exc


def next_id(
    name: str,
    key: str,
) -> int:
    data = load_json(name)

    value = int(
        data.get(key, 1)
    )

    if value < 1:
        value = 1

    data[key] = value + 1

    save_json(
        name,
        data,
    )

    return value


def get_list(
    name: str,
    key: str,
) -> list:
    data = load_json(name)

    value = data.get(
        key,
        [],
    )

    if not isinstance(value, list):
        raise RuntimeError(
            f"الحقل {key} في {name} ليس قائمة"
        )

    return value


def save_list(
    name: str,
    key: str,
    items: list,
):
    if not isinstance(items, list):
        raise TypeError(
            "items يجب أن تكون قائمة"
        )

    data = load_json(name)

    data[key] = items

    save_json(
        name,
        data,
    )


def append_item(
    name: str,
    key: str,
    item: dict,
):
    if not isinstance(item, dict):
        raise TypeError(
            "السجل يجب أن يكون dict"
        )

    data = load_json(name)

    items = data.get(
        key,
        [],
    )

    if not isinstance(items, list):
        raise RuntimeError(
            f"الحقل {key} في {name} ليس قائمة"
        )

    items.append(item)

    data[key] = items

    save_json(
        name,
        data,
    )


def find_by_id(
    name: str,
    key: str,
    field: str,
    value: Any,
):
    items = get_list(
        name,
        key,
    )

    for item in items:
        if item.get(field) == value:
            return item

    return None
