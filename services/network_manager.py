from datetime import datetime
from services.storage import load_json, save_json


DATA_FILE = "networks"


def _now():
    return datetime.now().isoformat()


def _load():
    data = load_json(DATA_FILE)

    if "networks" not in data:
        data["networks"] = []

    return data


def _save(data):
    save_json(DATA_FILE, data)


def _next_network_id(data):
    ids = []

    for network in data["networks"]:
        try:
            ids.append(int(network.get("network_id", 0)))
        except (TypeError, ValueError):
            pass

    return max(ids, default=0) + 1


def get_network(network_id):
    network_id = int(network_id)

    data = _load()

    for network in data["networks"]:
        if int(network.get("network_id", 0)) == network_id:
            return network

    return None


def get_networks():
    data = _load()
    return list(data["networks"])


def get_networks_by_owner(owner_user_id):
    owner_user_id = int(owner_user_id)

    return [
        network
        for network in get_networks()
        if int(network.get("owner_user_id", 0)) == owner_user_id
    ]


def get_pending_networks():
    return [
        network
        for network in get_networks()
        if network.get("status") == "pending"
    ]


def get_approved_networks():
    return [
        network
        for network in get_networks()
        if network.get("status") == "approved"
    ]


def create_network_request(
    owner_user_id,
    network_name,
    area,
    owner_name=None,
    phone=None,
):
    owner_user_id = int(owner_user_id)

    network_name = str(network_name or "").strip()
    area = str(area or "").strip()

    if not network_name:
        raise ValueError("اسم الشبكة مطلوب")

    if not area:
        raise ValueError("المنطقة مطلوبة")

    data = _load()

    for network in data["networks"]:
        if (
            int(network.get("owner_user_id", 0)) == owner_user_id
            and network.get("network_name", "").strip() == network_name
            and network.get("status") in ("pending", "approved")
        ):
            raise ValueError("لديك طلب أو شبكة بهذا الاسم مسبقًا")

    network_id = _next_network_id(data)
    now = _now()

    network = {
        "network_id": network_id,
        "owner_user_id": owner_user_id,
        "owner_name": str(owner_name or "").strip(),
        "network_name": network_name,
        "area": area,
        "phone": str(phone or "").strip(),
        "status": "pending",
        "created_at": now,
        "reviewed_at": None,
        "reviewed_by": None,
        "rejection_reason": None,
    }

    data["networks"].append(network)

    _save(data)

    return network


def approve_network(network_id, admin_user_id):
    network_id = int(network_id)
    admin_user_id = int(admin_user_id)

    data = _load()

    target = None

    for network in data["networks"]:
        if int(network.get("network_id", 0)) == network_id:
            target = network
            break

    if target is None:
        raise ValueError("الشبكة غير موجودة")

    if target.get("status") == "approved":
        raise ValueError("الشبكة معتمدة مسبقًا")

    if target.get("status") != "pending":
        raise ValueError("لا يمكن اعتماد هذه الشبكة في حالتها الحالية")

    now = _now()

    target["status"] = "approved"
    target["reviewed_at"] = now
    target["reviewed_by"] = admin_user_id
    target["rejection_reason"] = None

    _save(data)

    return target


def reject_network(
    network_id,
    admin_user_id,
    reason="",
):
    network_id = int(network_id)
    admin_user_id = int(admin_user_id)

    reason = str(reason or "").strip()

    data = _load()

    target = None

    for network in data["networks"]:
        if int(network.get("network_id", 0)) == network_id:
            target = network
            break

    if target is None:
        raise ValueError("الشبكة غير موجودة")

    if target.get("status") != "pending":
        raise ValueError("لا يمكن رفض هذه الشبكة في حالتها الحالية")

    now = _now()

    target["status"] = "rejected"
    target["reviewed_at"] = now
    target["reviewed_by"] = admin_user_id
    target["rejection_reason"] = reason or "تم رفض الطلب من الإدارة"

    _save(data)

    return target


def reopen_network_request(network_id):
    network_id = int(network_id)

    data = _load()

    target = None

    for network in data["networks"]:
        if int(network.get("network_id", 0)) == network_id:
            target = network
            break

    if target is None:
        raise ValueError("الشبكة غير موجودة")

    if target.get("status") != "rejected":
        raise ValueError("إعادة الطلب متاحة للطلبات المرفوضة فقط")

    target["status"] = "pending"
    target["reviewed_at"] = None
    target["reviewed_by"] = None
    target["rejection_reason"] = None

    _save(data)

    return target
