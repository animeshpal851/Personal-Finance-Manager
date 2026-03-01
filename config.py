"""Application configuration."""

import os

# MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DB_NAME", "personal_finance_db")

# Collections
TRANSACTIONS_COLLECTION = "transactions"
BUDGETS_COLLECTION = "budgets"
GOALS_COLLECTION = "savings_goals"

# Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "finance-secret-key-2024")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

# Logging
LOG_FILE = "logs/app.log"
LOG_LEVEL = "INFO"

# Budget alert thresholds
BUDGET_ALERT_THRESHOLDS = [0.70, 0.90, 1.00]

# Analytics
ANOMALY_MULTIPLIER = 2.0
HEALTH_SCORE_WEIGHTS = {
    "savings_rate": 40,
    "budget_adherence": 30,
    "expense_stability": 30,
}

# Categories
INCOME_CATEGORIES = [
    "Salary", "Freelance", "Business", "Investment",
    "Rental", "Bonus", "Gift", "Other Income"
]

EXPENSE_CATEGORIES = [
    "Food", "Housing", "Transport", "Utilities",
    "Healthcare", "Entertainment", "Shopping",
    "Education", "Travel", "Savings", "Other Expense"
]

CURRENCY_SYMBOL = "₹"
