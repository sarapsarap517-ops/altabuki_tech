from datetime import datetime
from hashlib import sha256

from services.storage import (
    load_json,
    save_json,
    next_id,
)


# =========================================================
# الثوابت
# =========================================================

USERS_FILE = "users"
USERS_KEY = "users"

ROLE_CUSTOMER = "customer"
ROLE_NETWORK_OWNER = "network_owner"
ROLE_ADMIN = "admin"

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_SUSPENDED = "suspended"


# =========================================================
# أدوات داخلية
# =========================================================

def _now():
    return datetime.now().isoformat()


def _normalize_phone(phone):
    return str(phone or "").strip()


def _normalize_text(value):
    return str(value or "").strip()


def _hash_password(password):
    password = str(password or "")

    return sha256(
        password.encode("utf-8")
    ).hexdigest()


def _get_users():
    data = load_json(USERS_FILE)

    users = data.get(
        USERS_KEY,
        [],
    )

    if not isinstance(users, list):
        raise RuntimeError(
            "بيانات المستخدمين غير صحيحة"
        )

    return users


def _save_users(users):
    data = load_json(USERS_FILE)
    data[USERS_KEY] = users
    save_json(
        USERS_FILE,
        data,
    )


# =========================================================
# البحث
# =========================================================

def get_user_by_id(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    for user in _get_users():
        if user.get("user_id") == user_id:
            return user

    return None


def get_user_by_phone(phone):
    phone = _normalize_phone(phone)

    if not phone:
        return None

    for user in _get_users():
        if (
            _normalize_phone(
                user.get("phone")
            )
            == phone
        ):
            return user

    return None


def get_users():
    return list(_get_users())


def get_users_by_status(status):
    status = _normalize_text(status)

    return [
        user
        for user in _get_users()
        if user.get("status") == status
    ]


# =========================================================
# التسجيل
# =========================================================

def register_user(
    name,
    phone,
    password,
    id_image=None,
    id_front_image=None,
    id_back_image=None,
    passport_image=None,
):
    name = _normalize_text(name)
    phone = _normalize_phone(phone)
    password = str(password or "").strip()

    if not name:
        raise ValueError(
            "الاسم مطلوب"
        )

    if not phone:
        raise ValueError(
            "رقم الهاتف مطلوب"
        )

    if not password:
        raise ValueError(
            "كلمة المرور مطلوبة"
        )

    if len(password) < 4:
        raise ValueError(
            "كلمة المرور قصيرة جدًا"
        )

    if get_user_by_phone(phone):
        raise ValueError(
            "رقم الهاتف مسجل مسبقًا"
        )

    user_id = next_id(
        USERS_FILE,
        "next_user_id",
    )

    user = {
        "user_id": user_id,
        "name": name,
        "phone": phone,
        "password_hash": _hash_password(
            password
        ),
        "id_image": id_image,
        "id_front_image": id_front_image,
        "id_back_image": id_back_image,
        "passport_image": passport_image,
        "favorite_network_ids": [],
        "role": ROLE_CUSTOMER,
        "status": STATUS_PENDING,
        "created_at": _now(),
        "reviewed_at": None,
        "reviewed_by": None,
        "rejection_reason": None,
    }

    users = _get_users()
    users.append(user)
    _save_users(users)

    return user



def update_user(user_id, **changes):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("الحساب غير موجود")
    users = _get_users()
    for i, item in enumerate(users):
        if int(item.get("user_id", 0)) == int(user_id):
            item.update(changes)
            users[i] = item
            _save_users(users)
            return item
    raise ValueError("الحساب غير موجود")


def set_favorite_network(user_id, network_id, favorite=True):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("الحساب غير موجود")
    ids = set(int(x) for x in (user.get("favorite_network_ids") or []))
    nid = int(network_id)
    if favorite: ids.add(nid)
    else: ids.discard(nid)
    return update_user(user_id, favorite_network_ids=sorted(ids))

# =========================================================
# تسجيل الدخول
# =========================================================

def authenticate_user(
    phone,
    password,
):
    phone = _normalize_phone(phone)
    password = str(password or "")

    user = get_user_by_phone(phone)

    if not user:
        raise ValueError(
            "رقم الهاتف أو كلمة المرور غير صحيحة"
        )

    if user.get("status") != STATUS_APPROVED:
        status = user.get("status")

        if status == STATUS_PENDING:
            raise ValueError(
                "الحساب بانتظار مراجعة الإدارة"
            )

        if status == STATUS_REJECTED:
            reason = user.get(
                "rejection_reason"
            )

            if reason:
                raise ValueError(
                    f"تم رفض الحساب: {reason}"
                )

            raise ValueError(
                "تم رفض الحساب"
            )

        if status == STATUS_SUSPENDED:
            raise ValueError(
                "الحساب موقوف"
            )

        raise ValueError(
            "الحساب غير متاح للدخول"
        )

    password_hash = _hash_password(
        password
    )

    if user.get(
        "password_hash"
    ) != password_hash:
        raise ValueError(
            "رقم الهاتف أو كلمة المرور غير صحيحة"
        )

    return user


# =========================================================
# مراجعة الإدارة
# =========================================================

def approve_user(
    user_id,
    admin_user_id=None,
):
    user = get_user_by_id(user_id)

    if not user:
        raise ValueError(
            "الحساب غير موجود"
        )

    if user.get("status") == STATUS_APPROVED:
        return user

    if user.get("status") == STATUS_SUSPENDED:
        raise ValueError(
            "لا يمكن اعتماد حساب موقوف"
        )

    user["status"] = STATUS_APPROVED
    user["reviewed_at"] = _now()
    user["reviewed_by"] = admin_user_id
    user["rejection_reason"] = None

    users = _get_users()

    for index, item in enumerate(users):
        if item.get("user_id") == user["user_id"]:
            users[index] = user
            break

    _save_users(users)

    return user


def reject_user(
    user_id,
    admin_user_id=None,
    reason=None,
):
    user = get_user_by_id(user_id)

    if not user:
        raise ValueError(
            "الحساب غير موجود"
        )

    if user.get("status") == STATUS_APPROVED:
        raise ValueError(
            "الحساب معتمد بالفعل"
        )

    user["status"] = STATUS_REJECTED
    user["reviewed_at"] = _now()
    user["reviewed_by"] = admin_user_id
    user["rejection_reason"] = (
        _normalize_text(reason)
        or None
    )

    users = _get_users()

    for index, item in enumerate(users):
        if item.get("user_id") == user["user_id"]:
            users[index] = user
            break

    _save_users(users)

    return user


def suspend_user(
    user_id,
    admin_user_id=None,
):
    user = get_user_by_id(user_id)

    if not user:
        raise ValueError(
            "الحساب غير موجود"
        )

    user["status"] = STATUS_SUSPENDED
    user["reviewed_at"] = _now()
    user["reviewed_by"] = admin_user_id

    users = _get_users()

    for index, item in enumerate(users):
        if item.get("user_id") == user["user_id"]:
            users[index] = user
            break

    _save_users(users)

    return user


# =========================================================
# ترقية صاحب شبكة
# =========================================================

def set_network_owner(
    user_id,
    admin_user_id=None,
):
    user = get_user_by_id(user_id)

    if not user:
        raise ValueError(
            "الحساب غير موجود"
        )

    if user.get("status") != STATUS_APPROVED:
        raise ValueError(
            "لا يمكن تحويل حساب غير معتمد"
        )

    user["role"] = ROLE_NETWORK_OWNER
    user["reviewed_at"] = _now()
    user["reviewed_by"] = admin_user_id

    users = _get_users()

    for index, item in enumerate(users):
        if item.get("user_id") == user["user_id"]:
            users[index] = user
            break

    _save_users(users)

    return user


# =========================================================
# التحقق من صلاحيات الحساب
# =========================================================

def is_approved_user(user_id):
    user = get_user_by_id(user_id)

    return bool(
        user
        and user.get("status")
        == STATUS_APPROVED
    )


def has_role(
    user_id,
    role,
):
    user = get_user_by_id(user_id)

    if not user:
        return False

    return (
        user.get("role")
        == role
    )


def is_admin(user_id):
    return has_role(
        user_id,
        ROLE_ADMIN,
    )


def is_network_owner(user_id):
    return has_role(
        user_id,
        ROLE_NETWORK_OWNER,
    )


# =========================================================
# إخفاء البيانات الحساسة عند عرض الحساب
# =========================================================

def public_user(user):
    if not user:
        return None

    return {
        "user_id": user.get("user_id"),
        "name": user.get("name"),
        "phone": user.get("phone"),
        "role": user.get("role"),
        "status": user.get("status"),
        "id_image": user.get("id_image"),
        "created_at": user.get("created_at"),
        "reviewed_at": user.get("reviewed_at"),
        "reviewed_by": user.get("reviewed_by"),
        "rejection_reason": user.get(
            "rejection_reason"
        ),
    }
