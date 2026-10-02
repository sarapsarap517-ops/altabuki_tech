from datetime import datetime
from services.storage import load_json, save_json


DATA_FILE = "wallets"


def _now():
    return datetime.now().isoformat()


def _load():
    data = load_json(DATA_FILE)

    if "wallets" not in data:
        data["wallets"] = []

    return data


def _save(data):
    save_json(DATA_FILE, data)


def get_wallet(user_id):
    user_id = int(user_id)

    data = _load()

    for wallet in data["wallets"]:
        if int(wallet.get("user_id", 0)) == user_id:
            return wallet

    return None


def create_wallet(user_id):
    user_id = int(user_id)

    existing = get_wallet(user_id)

    if existing:
        return existing

    data = _load()

    wallet = {
        "wallet_id": len(data["wallets"]) + 1,
        "user_id": user_id,
        "balance": 0,
        "created_at": _now(),
        "updated_at": _now(),
    }

    data["wallets"].append(wallet)
    _save(data)

    return wallet


def get_or_create_wallet(user_id):
    wallet = get_wallet(user_id)

    if wallet:
        return wallet

    return create_wallet(user_id)


def get_balance(user_id):
    wallet = get_or_create_wallet(user_id)

    return float(wallet.get("balance", 0))


def deposit(user_id, amount):
    amount = float(amount)

    if amount <= 0:
        raise ValueError("مبلغ الإيداع يجب أن يكون أكبر من صفر")

    wallet = get_or_create_wallet(user_id)

    wallet["balance"] = float(wallet.get("balance", 0)) + amount
    wallet["updated_at"] = _now()

    data = _load()

    for item in data["wallets"]:
        if int(item["wallet_id"]) == int(wallet["wallet_id"]):
            item.update(wallet)
            break

    _save(data)

    return wallet


def withdraw(user_id, amount):
    amount = float(amount)

    if amount <= 0:
        raise ValueError("مبلغ السحب يجب أن يكون أكبر من صفر")

    wallet = get_or_create_wallet(user_id)

    balance = float(wallet.get("balance", 0))

    if balance < amount:
        raise ValueError("الرصيد غير كافٍ")

    wallet["balance"] = balance - amount
    wallet["updated_at"] = _now()

    data = _load()

    for item in data["wallets"]:
        if int(item["wallet_id"]) == int(wallet["wallet_id"]):
            item.update(wallet)
            break

    _save(data)

    return wallet


def transfer(from_user_id, to_user_id, amount):
    from_user_id = int(from_user_id)
    to_user_id = int(to_user_id)
    amount = float(amount)

    if from_user_id == to_user_id:
        raise ValueError("لا يمكن التحويل إلى نفس الحساب")

    if amount <= 0:
        raise ValueError("مبلغ التحويل يجب أن يكون أكبر من صفر")

    data = _load()

    sender = None
    receiver = None

    for wallet in data["wallets"]:
        uid = int(wallet.get("user_id", 0))

        if uid == from_user_id:
            sender = wallet

        if uid == to_user_id:
            receiver = wallet

    if sender is None:
        sender = {
            "wallet_id": len(data["wallets"]) + 1,
            "user_id": from_user_id,
            "balance": 0,
            "created_at": _now(),
            "updated_at": _now(),
        }
        data["wallets"].append(sender)

    if receiver is None:
        receiver = {
            "wallet_id": len(data["wallets"]) + 1,
            "user_id": to_user_id,
            "balance": 0,
            "created_at": _now(),
            "updated_at": _now(),
        }
        data["wallets"].append(receiver)

    sender_balance = float(sender.get("balance", 0))

    if sender_balance < amount:
        raise ValueError("الرصيد غير كافٍ للتحويل")

    sender["balance"] = sender_balance - amount
    receiver["balance"] = float(receiver.get("balance", 0)) + amount

    now = _now()

    sender["updated_at"] = now
    receiver["updated_at"] = now

    _save(data)

    return {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "amount": amount,
        "from_balance": sender["balance"],
        "to_balance": receiver["balance"],
        "created_at": now,
    }


def set_balance(user_id, amount):
    amount = float(amount)

    if amount < 0:
        raise ValueError("الرصيد لا يمكن أن يكون سالبًا")

    wallet = get_or_create_wallet(user_id)

    wallet["balance"] = amount
    wallet["updated_at"] = _now()

    data = _load()

    for item in data["wallets"]:
        if int(item["wallet_id"]) == int(wallet["wallet_id"]):
            item.update(wallet)
            break

    _save(data)

    return wallet
