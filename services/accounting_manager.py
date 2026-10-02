from services.storage import load_json


def get_all_entries():
    data = load_json("accounting")
    return list(data.get("entries", []))


def get_entry(entry_id):
    entry_id = int(entry_id)

    for entry in get_all_entries():
        if int(entry.get("entry_id", 0)) == entry_id:
            return entry

    return None


def get_entries_for_user(user_id):
    user_id = int(user_id)
    result = []

    for entry in get_all_entries():
        buyer_id = entry.get("buyer_user_id")
        owner_id = entry.get("owner_user_id")

        if buyer_id is not None and int(buyer_id) == user_id:
            result.append(entry)
            continue

        if owner_id is not None and int(owner_id) == user_id:
            result.append(entry)

    return result


def get_entries_for_network(network_id):
    network_id = int(network_id)

    return [
        entry
        for entry in get_all_entries()
        if int(entry.get("network_id", 0)) == network_id
    ]


def get_entries_for_package(package_id):
    package_id = int(package_id)

    return [
        entry
        for entry in get_all_entries()
        if int(entry.get("package_id", 0)) == package_id
    ]


def calculate_totals(entries=None):
    if entries is None:
        entries = get_all_entries()

    total_sales = 0.0
    total_owner = 0.0
    total_admin = 0.0
    total_quantity = 0

    for entry in entries:
        total_sales += float(entry.get("debit", 0))
        total_owner += float(entry.get("owner_credit", 0))
        total_admin += float(entry.get("admin_credit", 0))
        total_quantity += int(entry.get("quantity", 0))

    return {
        "total_sales": total_sales,
        "total_owner": total_owner,
        "total_admin": total_admin,
        "total_quantity": total_quantity,
        "entries_count": len(entries),
    }


def get_user_accounting_summary(user_id):
    entries = get_entries_for_user(user_id)

    purchases = 0.0
    owner_income = 0.0
    quantity = 0

    for entry in entries:
        buyer_id = entry.get("buyer_user_id")
        owner_id = entry.get("owner_user_id")

        if buyer_id is not None and int(buyer_id) == int(user_id):
            purchases += float(entry.get("debit", 0))

        if owner_id is not None and int(owner_id) == int(user_id):
            owner_income += float(entry.get("owner_credit", 0))

        quantity += int(entry.get("quantity", 0))

    return {
        "user_id": int(user_id),
        "purchases": purchases,
        "owner_income": owner_income,
        "quantity": quantity,
        "entries_count": len(entries),
    }


def get_network_summary(network_id):
    entries = get_entries_for_network(network_id)
    result = calculate_totals(entries)
    result["network_id"] = int(network_id)
    return result


def get_package_summary(package_id):
    entries = get_entries_for_package(package_id)
    result = calculate_totals(entries)
    result["package_id"] = int(package_id)
    return result
