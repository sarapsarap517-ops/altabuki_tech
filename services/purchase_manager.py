from datetime import datetime
from services.storage import load_json, save_json
from services.platform_wallet import credit as credit_platform


# =========================================================
# أدوات داخلية
# =========================================================

def _now():
    return datetime.now().isoformat()


def _next_id(data, key):
    value = int(data.get(key, 1))
    data[key] = value + 1
    return value


def _wallet(data, user_id):
    for wallet in data.get("wallets", []):
        if int(wallet.get("user_id", 0)) == int(user_id):
            return wallet
    return None


def _network(data, network_id):
    for network in data.get("networks", []):
        if int(network.get("network_id", 0)) == int(network_id):
            return network
    return None


def _package(data, package_id):
    for package in data.get("packages", []):
        if int(package.get("package_id", 0)) == int(package_id):
            return package
    return None


# =========================================================
# حساب سعر الشراء
# =========================================================

def calculate_purchase(
    package_id,
    quantity,
    network_id,
    commission_percent=None,
):
    if int(quantity) <= 0:
        raise ValueError("عدد الكروت يجب أن يكون أكبر من صفر")

    packages = load_json("packages")
    networks = load_json("networks")

    package = _package(packages, package_id)

    if package is None:
        raise ValueError("الباقة غير موجودة")

    network = _network(networks, network_id)

    if network is None:
        raise ValueError("الشبكة غير موجودة")

    if network.get("status") != "approved":
        raise ValueError("الشبكة غير معتمدة")

    price = float(
        package.get("price", 0)
    )

    if price <= 0:
        raise ValueError("سعر الباقة غير صحيح")

    quantity = int(quantity)

    total_amount = price * quantity

    if commission_percent is None:
        commission_percent = network.get(
            "commission_percent",
            network.get("commission", 10)
        )

    commission_percent = float(
        commission_percent
    )

    if commission_percent < 0 or commission_percent > 100:
        raise ValueError("نسبة العمولة غير صحيحة")

    commission = (
        total_amount
        * commission_percent
        / 100
    )

    owner_amount = (
        total_amount
        - commission
    )

    return {
        "package_id": int(package_id),
        "network_id": int(network_id),
        "quantity": quantity,
        "unit_price": price,
        "total_amount": total_amount,
        "commission_percent": commission_percent,
        "commission": commission,
        "owner_amount": owner_amount,
    }


# =========================================================
# تنفيذ عملية الشراء
#
# مهم:
# buyer_user_id = صاحب الحساب الذي يدفع
# beneficiary_phone = رقم المستفيد الذي ستصل إليه بيانات الكروت
#
# لا نفترض أن رقم المستفيد هو رقم صاحب الحساب.
# =========================================================

def purchase_cards(
    buyer_user_id,
    beneficiary_phone,
    network_id,
    package_id,
    quantity,
):
    buyer_user_id = int(buyer_user_id)
    network_id = int(network_id)
    package_id = int(package_id)
    quantity = int(quantity)

    if quantity <= 0:
        raise ValueError("عدد الكروت غير صحيح")

    beneficiary_phone = str(
        beneficiary_phone or ""
    ).strip()

    if not beneficiary_phone:
        raise ValueError(
            "رقم المستفيد مطلوب لإرسال بيانات الكروت"
        )

    packages = load_json("packages")
    networks = load_json("networks")
    wallets = load_json("wallets")
    cards = load_json("cards")
    transactions = load_json("transactions")
    accounting = load_json("accounting")

    package = _package(
        packages,
        package_id
    )

    if package is None:
        raise ValueError("الباقة غير موجودة")

    network = _network(
        networks,
        network_id
    )

    if network is None:
        raise ValueError("الشبكة غير موجودة")

    if network.get("status") != "approved":
        raise ValueError("الشبكة غير معتمدة")

    buyer_wallet = _wallet(
        wallets,
        buyer_user_id
    )

    if buyer_wallet is None:
        raise ValueError(
            "محفظة المشتري غير موجودة"
        )

    calculation = calculate_purchase(
        package_id=package_id,
        quantity=quantity,
        network_id=network_id,
    )

    total_amount = calculation["total_amount"]
    commission = calculation["commission"]
    owner_amount = calculation["owner_amount"]

    balance = float(
        buyer_wallet.get("balance", 0)
    )

    if balance < total_amount:
        raise ValueError(
            f"الرصيد غير كافي. "
            f"المطلوب: {total_amount:g} "
            f"| المتوفر: {balance:g}"
        )

    # -----------------------------------------------------
    # البحث عن الكروت قبل خصم الرصيد
    # -----------------------------------------------------

    available_cards = []

    for card in cards.get("cards", []):
        if (
            int(card.get("package_id", 0))
            == package_id
            and card.get("status") == "available"
        ):
            available_cards.append(card)

        if len(available_cards) >= quantity:
            break

    if len(available_cards) < quantity:
        raise ValueError(
            "عدد الكروت المتاحة غير كافٍ"
        )

    # -----------------------------------------------------
    # تحديد صاحب الشبكة
    # -----------------------------------------------------

    owner_user_id = network.get(
        "owner_user_id"
    )

    if owner_user_id is None:
        raise ValueError(
            "الشبكة غير مرتبطة بصاحب شبكة"
        )

    owner_wallet = _wallet(
        wallets,
        owner_user_id
    )

    if owner_wallet is None:
        raise ValueError(
            "محفظة صاحب الشبكة غير موجودة"
        )

    # -----------------------------------------------------
    # حساب الإدارة
    #
    # لا نفترض وجود مستخدم إداري محدد.
    # العمولة تسجل كحصة إدارية في العملية.
    # -----------------------------------------------------

    transaction_id = _next_id(
        transactions,
        "next_transaction_id"
    )

    accounting_id = _next_id(
        accounting,
        "next_entry_id"
    )

    # -----------------------------------------------------
    # حفظ الحالة الأصلية للتراجع الآمن
    # -----------------------------------------------------

    buyer_old_balance = balance
    owner_old_balance = float(
        owner_wallet.get("balance", 0)
    )

    sold_cards = []

    try:

        # خصم المشتري
        buyer_wallet["balance"] = (
            buyer_old_balance
            - total_amount
        )

        # إضافة حصة صاحب الشبكة
        owner_wallet["balance"] = (
            owner_old_balance
            + owner_amount
        )

        # تثبيت بيع الكروت
        for card in available_cards:

            card["status"] = "sold"

            card["sold_at"] = _now()

            card["customer_phone"] = (
                beneficiary_phone
            )

            card["buyer_user_id"] = (
                buyer_user_id
            )

            card["network_id"] = (
                network_id
            )

            card["transaction_id"] = (
                transaction_id
            )

            sold_cards.append(card)

        # -------------------------------------------------
        # الحركة المالية
        # -------------------------------------------------

        transaction = {
            "transaction_id": transaction_id,
            "type": "card_purchase",

            "buyer_user_id": buyer_user_id,

            # رقم المستفيد ليس هوية الحساب
            "beneficiary_phone": beneficiary_phone,

            "owner_user_id": owner_user_id,

            "network_id": network_id,
            "package_id": package_id,
            "quantity": quantity,

            "unit_price": calculation[
                "unit_price"
            ],

            "total_amount": total_amount,

            "commission_percent": calculation[
                "commission_percent"
            ],

            "commission": commission,

            "owner_amount": owner_amount,

            "card_ids": [
                int(card["card_id"])
                for card in sold_cards
            ],

            "status": "completed",

            "created_at": _now(),
        }

        transactions.setdefault(
            "transactions",
            []
        ).append(transaction)

        # -------------------------------------------------
        # الدفتر المحاسبي
        # -------------------------------------------------

        accounting_entry = {
            "entry_id": accounting_id,
            "transaction_id": transaction_id,
            "type": "card_purchase",

            "buyer_user_id": buyer_user_id,
            "owner_user_id": owner_user_id,

            "network_id": network_id,
            "package_id": package_id,

            "debit": total_amount,
            "owner_credit": owner_amount,
            "admin_credit": commission,

            "beneficiary_phone": beneficiary_phone,

            "created_at": _now(),
        }

        accounting.setdefault(
            "entries",
            []
        ).append(accounting_entry)

        # -------------------------------------------------
        # الحفظ
        # -------------------------------------------------

        save_json(
            "wallets",
            wallets
        )

        save_json(
            "cards",
            cards
        )

        save_json(
            "transactions",
            transactions
        )

        save_json(
            "accounting",
            accounting
        )

        # عمولة المنصة تُضاف فعليًا إلى محفظة المنصة
        credit_platform(
            commission,
            reason="عمولة شراء كرت",
            transaction_id=transaction_id,
        )

    except Exception:

        # -----------------------------------------------
        # تراجع كامل داخل الذاكرة
        # -----------------------------------------------

        buyer_wallet["balance"] = (
            buyer_old_balance
        )

        owner_wallet["balance"] = (
            owner_old_balance
        )

        for card in sold_cards:
            card["status"] = "available"
            card["sold_at"] = None

            card.pop(
                "customer_phone",
                None
            )

            card.pop(
                "buyer_user_id",
                None
            )

            card.pop(
                "network_id",
                None
            )

            card.pop(
                "transaction_id",
                None
            )

        raise

    return {
        "success": True,
        "transaction": transaction,
        "accounting_entry": accounting_entry,
        "cards": sold_cards,
        "total_amount": total_amount,
        "commission": commission,
        "owner_amount": owner_amount,
    }


# =========================================================
# قراءة عملية
# =========================================================

def get_transaction(
    transaction_id
):
    data = load_json(
        "transactions"
    )

    for transaction in data.get(
        "transactions",
        []
    ):
        if int(
            transaction.get(
                "transaction_id",
                0
            )
        ) == int(transaction_id):
            return transaction

    return None
