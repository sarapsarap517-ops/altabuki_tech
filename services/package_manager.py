from datetime import datetime
from services.storage import load_json, save_json
from services.network_manager import get_network


DATA_FILE = "packages"


def _now():
    return datetime.now().isoformat()


def _load():
    data = load_json(DATA_FILE)

    if "packages" not in data:
        data["packages"] = []

    return data


def _save(data):
    save_json(DATA_FILE, data)


def _next_package_id(data):
    ids = []

    for package in data["packages"]:
        try:
            ids.append(int(package.get("package_id", 0)))
        except (TypeError, ValueError):
            pass

    return max(ids, default=0) + 1


def get_package(package_id):
    package_id = int(package_id)

    data = _load()

    for package in data["packages"]:
        if int(package.get("package_id", 0)) == package_id:
            return package

    return None


def get_packages_for_network(network_id):
    network_id = int(network_id)

    return [
        package
        for package in _load()["packages"]
        if int(package.get("network_id", 0)) == network_id
        and package.get("status") == "active"
    ]


def create_package(
    network_id,
    denomination,
    price,
    commission=0,
    name="",
    data_amount="",
    validity_days=0,
):
    network_id = int(network_id)
    denomination = float(denomination)
    price = float(price)
    commission = float(commission)
    validity_days = int(validity_days)

    if get_network(network_id) is None:
        raise ValueError("الشبكة غير موجودة")

    if denomination <= 0:
        raise ValueError("قيمة الباقة يجب أن تكون أكبر من صفر")

    if price <= 0:
        raise ValueError("سعر الباقة يجب أن يكون أكبر من صفر")

    if commission < 0:
        raise ValueError("العمولة لا يمكن أن تكون سالبة")

    if commission > price:
        raise ValueError("العمولة لا يمكن أن تكون أكبر من سعر الباقة")

    if validity_days < 0:
        raise ValueError("مدة الصلاحية غير صحيحة")

    data = _load()

    package_id = _next_package_id(data)

    package = {
        "package_id": package_id,
        "network_id": network_id,
        "name": str(name or "").strip(),
        "denomination": denomination,
        "price": price,
        "commission": commission,
        "data_amount": str(data_amount or "").strip(),
        "validity_days": validity_days,
        "status": "active",
        "created_at": _now(),
    }

    data["packages"].append(package)

    _save(data)

    return package


def deactivate_package(package_id):
    package_id = int(package_id)

    data = _load()

    for package in data["packages"]:
        if int(package.get("package_id", 0)) == package_id:
            package["status"] = "inactive"
            package["updated_at"] = _now()
            _save(data)
            return package

    raise ValueError("الباقة غير موجودة")
