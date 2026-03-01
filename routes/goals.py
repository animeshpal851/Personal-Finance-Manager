"""Savings goals routes."""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

from services.goal_service import GoalService

goals_bp = Blueprint("goals", __name__)
goal_svc = GoalService()


@goals_bp.route("/goals")
def index():
    goals = goal_svc.get_all_goals()
    return render_template("goals.html", goals=goals)


@goals_bp.route("/goals/create", methods=["POST"])
def create():
    try:
        name = request.form["name"]
        target = float(request.form["target_amount"])
        current = float(request.form.get("current_amount", 0))
        notes = request.form.get("notes", "")
        deadline = None
        dl = request.form.get("deadline", "")
        if dl:
            deadline = datetime.strptime(dl, "%Y-%m-%d")
        goal_svc.create_goal(name, target, deadline, current, notes)
        flash(f"🎯 Goal '{name}' created!", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
    return redirect(url_for("goals.index"))


@goals_bp.route("/goals/update/<goal_id>", methods=["POST"])
def update(goal_id):
    try:
        amount = float(request.form["current_amount"])
        goal = goal_svc.get_goal_by_id(goal_id)
        goal_svc.update_progress(goal_id, amount)
        if goal and amount >= goal["target_amount"]:
            flash(f"🎉 Goal completed!", "success")
        else:
            flash("✅ Progress updated!", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
    return redirect(url_for("goals.index"))


@goals_bp.route("/goals/delete/<goal_id>", methods=["POST"])
def delete(goal_id):
    goal_svc.delete_goal(goal_id)
    flash("🗑️ Goal deleted.", "info")
    return redirect(url_for("goals.index"))
