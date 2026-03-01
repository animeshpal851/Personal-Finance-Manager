"""Budget routes."""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

from services.budget_service import BudgetService
from models.budget import Budget
from config import EXPENSE_CATEGORIES

budgets_bp = Blueprint("budgets", __name__)
budget_svc = BudgetService()


@budgets_bp.route("/budgets")
def index():
    now = datetime.now()
    month = int(request.args.get("month", now.month))
    year = int(request.args.get("year", now.year))
    data = budget_svc.budget_vs_actual(month, year)
    all_budgets = budget_svc.get_all_budgets()
    return render_template(
        "budgets.html",
        data=data,
        month=month,
        year=year,
        all_budgets=all_budgets,
        categories=EXPENSE_CATEGORIES,
        now=now,
    )


@budgets_bp.route("/budgets/set", methods=["POST"])
def set_budget():
    try:
        category = request.form["category"]
        amount = float(request.form["amount"])
        month = int(request.form["month"])
        year = int(request.form["year"])
        b = Budget(category=category, limit_amount=amount, month=month, year=year)
        action = budget_svc.set_budget(b)
        flash(f"✅ Budget {action} for {category}!", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
    return redirect(url_for("budgets.index"))


@budgets_bp.route("/budgets/delete", methods=["POST"])
def delete_budget():
    category = request.form["category"]
    month = int(request.form["month"])
    year = int(request.form["year"])
    budget_svc.delete_budget(category, month, year)
    flash("🗑️ Budget deleted.", "info")
    return redirect(url_for("budgets.index"))
