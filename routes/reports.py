"""Report routes — monthly summary, category breakdown, analytics."""

from flask import Blueprint, render_template, jsonify
from services.report_service import ReportService
from services.analytics_service import AnalyticsService

reports_bp = Blueprint("reports", __name__)
report_svc = ReportService()
analytics_svc = AnalyticsService()


@reports_bp.route("/reports")
def index():
    monthly = report_svc.monthly_summary()
    category = report_svc.category_expense_summary()
    totals = report_svc.overall_totals()
    health = analytics_svc.financial_health_score()
    anomalies = analytics_svc.detect_anomalies()
    forecast = analytics_svc.savings_forecast(6)

    return render_template(
        "reports.html",
        monthly=monthly,
        category=category,
        totals=totals,
        health=health,
        anomalies=anomalies,
        forecast=forecast,
    )


# ── JSON API endpoints for Chart.js ──────────────────────────────────────────

@reports_bp.route("/api/monthly-summary")
def api_monthly():
    data = report_svc.monthly_summary()
    return jsonify(data)


@reports_bp.route("/api/category-expense")
def api_category():
    data = report_svc.category_expense_summary()
    return jsonify(data)


@reports_bp.route("/api/health-score")
def api_health():
    return jsonify(analytics_svc.financial_health_score())
