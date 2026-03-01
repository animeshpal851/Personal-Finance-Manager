"""Transaction routes — add, view, delete."""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from services.finance_service import FinanceService
from models.transaction import Transaction
from config import INCOME_CATEGORIES, EXPENSE_CATEGORIES

transactions_bp = Blueprint("transactions", __name__)
finance_svc = FinanceService()


@transactions_bp.route("/transactions")
def index():
    t_type = request.args.get("type", "")
    limit = int(request.args.get("limit", 50))
    transactions = finance_svc.get_all_transactions(
        limit=limit,
        transaction_type=t_type if t_type in ("income", "expense") else None,
    )
    return render_template(
        "transactions.html",
        transactions=transactions,
        filter_type=t_type,
        total=finance_svc.count_transactions(),
    )


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            t_type = request.form["type"].lower()
            category = request.form["category"]
            amount = float(request.form["amount"])
            date_str = request.form["date"]
            description = request.form.get("description", "")
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            txn = Transaction(
                date=date_obj,
                transaction_type=t_type,
                category=category,
                amount=amount,
                description=description,
            )
            finance_svc.add_transaction(txn)
            flash(f"✅ {t_type.capitalize()} of ₹{amount:,.2f} added successfully!", "success")
            return redirect(url_for("transactions.index"))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "danger")

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template(
        "add_transaction.html",
        income_categories=INCOME_CATEGORIES,
        expense_categories=EXPENSE_CATEGORIES,
        today=today,
    )


@transactions_bp.route("/transactions/delete/<txn_id>", methods=["POST"])
def delete(txn_id):
    if finance_svc.delete_transaction(txn_id):
        flash("🗑️ Transaction deleted.", "info")
    else:
        flash("❌ Could not delete transaction.", "danger")
    return redirect(url_for("transactions.index"))


@transactions_bp.route("/api/transactions")
def api_list():
    transactions = finance_svc.get_all_transactions(limit=100)
    return jsonify([{
        "id": str(t._id),
        "date": t.date.strftime("%Y-%m-%d"),
        "type": t.transaction_type,
        "category": t.category,
        "amount": t.amount,
        "description": t.description,
    } for t in transactions])
