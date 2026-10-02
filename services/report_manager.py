from datetime import datetime

from services.storage import load_json


# =========================================================
# REPORT MANAGER
#
# مصدر التقرير:
#   transactions.json
#   accounting.json
#
# التقرير لا يعدل أي بيانات.
#
# المفاهيم:
#   user_id            = صاحب الحساب داخل التطبيق
#   beneficiary_phone  = رقم المستفيد الذي ستصل إليه بيانات الشراء
#
# كشف الحساب:
#   رصيد سابق
#   حركات
#   رصيد تراكمي
#   إجمالي
#   رصيد نهائي
# =========================================================


def _transactions():
    data = load_json("transactions")
    return list(data.get("transactions", []))


def _accounting():
    data = load_json("accounting")
    return list(data.get("entries", []))


def _number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _integer(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _text(value):
    return str(value or "").strip()


def _date_value(item):
    value = (
        item.get("created_at")
        or item.get("date")
        or item.get("transaction_date")
        or item.get("timestamp")
        or ""
    )

    return _text(value)


def _sort_key(item):
    return _date_value(item)


def _transaction_id(item):
    return (
        item.get("transaction_id")
        or item.get("id")
        or item.get("purchase_id")
        or ""
    )


def _network_name(item):
    return _text(
        item.get("network_name")
        or item.get("network")
        or ""
    )


def _package_name(item):
    return _text(
        item.get("package_name")
        or item.get("package")
        or item.get("package_title")
        or ""
    )


def _beneficiary_phone(item):
    return _text(
        item.get("beneficiary_phone")
        or item.get("customer_phone")
        or item.get("recipient_phone")
        or ""
    )


def _quantity(item):
    return _integer(
        item.get("quantity")
        or item.get("cards_count")
        or item.get("count")
        or 0
    )


def _amount(item):
    return _number(
        item.get("total_amount")
        or item.get("amount")
        or item.get("debit")
        or 0
    )


def _commission(item):
    return _number(
        item.get("commission")
        or item.get("total_commission")
        or 0
    )


def _owner_amount(item):
    return _number(
        item.get("owner_amount")
        or item.get("owner_credit")
        or 0
    )


def _status(item):
    return _text(
        item.get("status")
        or "completed"
    )


# =========================================================
# العمليات
# =========================================================

def get_all_transactions():
    return sorted(
        _transactions(),
        key=_sort_key
    )


def get_transaction(transaction_id):
    wanted = str(transaction_id)

    for item in get_all_transactions():
        if str(_transaction_id(item)) == wanted:
            return item

    return None


def get_user_transactions(user_id):
    user_id = int(user_id)
    result = []

    for item in get_all_transactions():

        buyer_id = item.get(
            "buyer_user_id"
        )

        owner_id = item.get(
            "owner_user_id"
        )

        if buyer_id is not None:
            if _integer(buyer_id) == user_id:
                result.append(item)
                continue

        if owner_id is not None:
            if _integer(owner_id) == user_id:
                result.append(item)

    return result


def get_network_transactions(network_id):
    network_id = int(network_id)

    return [
        item
        for item in get_all_transactions()
        if _integer(
            item.get("network_id")
        ) == network_id
    ]


def get_package_transactions(package_id):
    package_id = int(package_id)

    return [
        item
        for item in get_all_transactions()
        if _integer(
            item.get("package_id")
        ) == package_id
    ]


def get_beneficiary_transactions(
    beneficiary_phone
):
    wanted = _text(
        beneficiary_phone
    )

    return [
        item
        for item in get_all_transactions()
        if _beneficiary_phone(item) == wanted
    ]


# =========================================================
# وصف البيان
# =========================================================

def build_transaction_description(
    transaction
):
    network = _network_name(
        transaction
    )

    package = _package_name(
        transaction
    )

    quantity = _quantity(
        transaction
    )

    beneficiary = _beneficiary_phone(
        transaction
    )

    transaction_id = _transaction_id(
        transaction
    )

    parts = []

    if network:
        parts.append(
            f"الشبكة: {network}"
        )

    if package:
        parts.append(
            f"الباقة: {package}"
        )

    if quantity:
        parts.append(
            f"عدد الكروت: {quantity}"
        )

    if beneficiary:
        parts.append(
            f"المستفيد: {beneficiary}"
        )

    if transaction_id:
        parts.append(
            f"رقم العملية: {transaction_id}"
        )

    if not parts:
        parts.append(
            "عملية مالية"
        )

    return " | ".join(parts)


# =========================================================
# تحويل العملية إلى سطر تقرير
# =========================================================

def transaction_to_report_row(
    transaction,
    running_balance=0.0
):
    amount = _amount(
        transaction
    )

    status = _status(
        transaction
    )

    debit = 0.0
    credit = 0.0

    # عملية شراء العميل = عليه
    if status == "completed":
        debit = amount

    return {
        "transaction_id":
            _transaction_id(transaction),

        "date":
            _date_value(transaction),

        "description":
            build_transaction_description(
                transaction
            ),

        "debit":
            debit,

        "credit":
            credit,

        "amount":
            amount,

        "commission":
            _commission(transaction),

        "owner_amount":
            _owner_amount(transaction),

        "beneficiary_phone":
            _beneficiary_phone(transaction),

        "network_id":
            transaction.get(
                "network_id"
            ),

        "package_id":
            transaction.get(
                "package_id"
            ),

        "quantity":
            _quantity(transaction),

        "status":
            status,

        "balance":
            running_balance,
    }


# =========================================================
# كشف حساب العميل
# =========================================================

def get_customer_statement(
    user_id,
    opening_balance=0.0
):
    transactions = get_user_transactions(
        user_id
    )

    transactions = sorted(
        transactions,
        key=_sort_key
    )

    balance = _number(
        opening_balance
    )

    rows = []

    total_debit = 0.0
    total_credit = 0.0

    for transaction in transactions:

        if _status(transaction) != "completed":
            continue

        amount = _amount(
            transaction
        )

        debit = amount
        credit = 0.0

        balance += credit
        balance -= debit

        total_debit += debit
        total_credit += credit

        row = transaction_to_report_row(
            transaction,
            running_balance=balance
        )

        row["debit"] = debit
        row["credit"] = credit
        row["balance"] = balance

        rows.append(row)

    return {
        "user_id": int(user_id),

        "opening_balance":
            _number(opening_balance),

        "rows":
            rows,

        "total_debit":
            total_debit,

        "total_credit":
            total_credit,

        "final_balance":
            balance,

        "entries_count":
            len(rows),
    }


# =========================================================
# كشف حساب صاحب الشبكة
# =========================================================

def get_owner_statement(
    user_id,
    opening_balance=0.0
):
    transactions = get_user_transactions(
        user_id
    )

    transactions = sorted(
        transactions,
        key=_sort_key
    )

    balance = _number(
        opening_balance
    )

    rows = []

    total_credit = 0.0
    total_debit = 0.0

    for transaction in transactions:

        if _status(transaction) != "completed":
            continue

        owner_amount = _owner_amount(
            transaction
        )

        if owner_amount <= 0:
            continue

        credit = owner_amount
        debit = 0.0

        balance += credit

        total_credit += credit
        total_debit += debit

        row = transaction_to_report_row(
            transaction,
            running_balance=balance
        )

        row["debit"] = debit
        row["credit"] = credit
        row["amount"] = owner_amount
        row["balance"] = balance

        rows.append(row)

    return {
        "user_id": int(user_id),

        "opening_balance":
            _number(opening_balance),

        "rows":
            rows,

        "total_debit":
            total_debit,

        "total_credit":
            total_credit,

        "final_balance":
            balance,

        "entries_count":
            len(rows),
    }


# =========================================================
# تقرير الشبكة
# =========================================================

def get_network_report(
    network_id
):
    transactions = get_network_transactions(
        network_id
    )

    completed = [
        item
        for item in transactions
        if _status(item) == "completed"
    ]

    total_amount = sum(
        _amount(item)
        for item in completed
    )

    total_commission = sum(
        _commission(item)
        for item in completed
    )

    total_owner = sum(
        _owner_amount(item)
        for item in completed
    )

    total_quantity = sum(
        _quantity(item)
        for item in completed
    )

    return {
        "network_id":
            int(network_id),

        "transactions_count":
            len(completed),

        "total_amount":
            total_amount,

        "total_commission":
            total_commission,

        "total_owner_amount":
            total_owner,

        "total_quantity":
            total_quantity,

        "transactions":
            completed,
    }


# =========================================================
# تقرير الفترة
# =========================================================

def get_period_report(
    start_date=None,
    end_date=None
):
    transactions = get_all_transactions()

    start = _text(
        start_date
    )

    end = _text(
        end_date
    )

    selected = []

    for transaction in transactions:

        date_value = _date_value(
            transaction
        )

        if start and date_value[:10] < start:
            continue

        if end and date_value[:10] > end:
            continue

        selected.append(
            transaction
        )

    completed = [
        item
        for item in selected
        if _status(item) == "completed"
    ]

    total_amount = sum(
        _amount(item)
        for item in completed
    )

    total_commission = sum(
        _commission(item)
        for item in completed
    )

    total_owner = sum(
        _owner_amount(item)
        for item in completed
    )

    total_quantity = sum(
        _quantity(item)
        for item in completed
    )

    return {
        "start_date": start,
        "end_date": end,

        "transactions_count":
            len(completed),

        "total_amount":
            total_amount,

        "total_commission":
            total_commission,

        "total_owner_amount":
            total_owner,

        "total_quantity":
            total_quantity,

        "transactions":
            completed,
    }


# =========================================================
# التقرير العام
# =========================================================

def get_dashboard_report():
    return get_period_report()


# =========================================================
# فحص التقرير
# =========================================================

def report_manager_health():
    transactions = get_all_transactions()
    accounting = _accounting()

    return {
        "transactions":
            len(transactions),

        "accounting_entries":
            len(accounting),

        "ready":
            True,
    }
