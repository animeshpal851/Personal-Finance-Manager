"""
Personal Finance Manager — Flask Web Application
=================================================
Run:
    python app.py
Then open: http://localhost:5000
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, redirect, url_for
from config import SECRET_KEY, DEBUG, LOG_FILE, LOG_LEVEL
from database.mongo_connection import connection
from services.report_service import ReportService
from services.finance_service import FinanceService
from services.analytics_service import AnalyticsService

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ── App factory ───────────────────────────────────────────────────────────────
def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Connect to MongoDB
    try:
        connection.connect()
        logger.info("MongoDB connected successfully.")
    except ConnectionError as exc:
        logger.error("MongoDB connection failed: %s", exc)
        raise

    # Register blueprints
    from routes.transactions import transactions_bp
    from routes.reports import reports_bp
    from routes.budgets import budgets_bp
    from routes.goals import goals_bp
    from routes.library import library_bp

    app.register_blueprint(transactions_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(library_bp)

    # ── Dashboard ─────────────────────────────────────────────────────────────
    @app.route("/")
    def dashboard():
        report_svc = ReportService()
        finance_svc = FinanceService()
        analytics_svc = AnalyticsService()

        totals = report_svc.overall_totals()
        monthly = report_svc.monthly_summary()
        category = report_svc.category_expense_summary()
        recent = finance_svc.get_all_transactions(limit=5)
        health = analytics_svc.financial_health_score()
        total_txns = finance_svc.count_transactions()

        # Current month data
        now = datetime.now()
        current_month_data = next(
            (m for m in monthly if m["month"] == now.month and m["year"] == now.year),
            {"total_income": 0, "total_expense": 0, "net_savings": 0}
        )

        return render_template(
            "dashboard.html",
            totals=totals,
            monthly=monthly,
            category=category,
            recent=recent,
            health=health,
            total_txns=total_txns,
            current_month=current_month_data,
            now=now,
        )

    # ── Template filters ──────────────────────────────────────────────────────
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except:
            return "₹0.00"

    @app.template_filter("month_name")
    def month_name_filter(month):
        names = ["Jan","Feb","Mar","Apr","May","Jun",
                 "Jul","Aug","Sep","Oct","Nov","Dec"]
        return names[int(month) - 1] if 1 <= int(month) <= 12 else str(month)

    @app.template_filter("date_fmt")
    def date_fmt_filter(dt):
        if dt:
            return dt.strftime("%d %b %Y")
        return ""

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "="*55)
    print("  💰  Personal Finance Manager")
    print("  🌐  http://localhost:5000")
    print("="*55 + "\n")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=DEBUG, host="0.0.0.0", port=port)
