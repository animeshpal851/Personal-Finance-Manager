<<<<<<< HEAD
# 💰 FinanceOS — Personal Finance Web App
### Flask + MongoDB + Chart.js

A full-stack personal finance web application with a dark, professional dashboard UI.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure MongoDB is running (localhost:27017)

# 3. Run the app
python app.py

# 4. Open browser
http://localhost:5000
```

---

## 📁 Project Structure

```
personal_finance_web/
│
├── app.py                  # Flask app factory + dashboard route
├── config.py               # All configuration constants
├── requirements.txt
│
├── database/
│   └── mongo_connection.py # MongoDB singleton
│
├── models/
│   ├── transaction.py
│   ├── budget.py
│   └── user.py
│
├── services/
│   ├── finance_service.py  # CRUD operations
│   ├── report_service.py   # MongoDB aggregations
│   ├── analytics_service.py# Health score + anomaly detection
│   ├── budget_service.py   # Budget thresholds
│   └── goal_service.py     # Savings goals
│
├── routes/
│   ├── transactions.py     # /transactions
│   ├── reports.py          # /reports
│   ├── budgets.py          # /budgets
│   └── goals.py            # /goals
│
├── templates/
│   ├── base.html           # Master layout + sidebar
│   ├── dashboard.html      # Main dashboard
│   ├── add_transaction.html
│   ├── transactions.html
│   ├── reports.html
│   ├── budgets.html
│   └── goals.html
│
└── static/
    ├── css/style.css       # Complete design system
    └── js/main.js          # Sidebar, charts, modals
```

---

## 🌐 Deploy to Railway (Free)

1. Create account at [railway.app](https://railway.app)
2. Push your code to GitHub
3. New Project → Deploy from GitHub
4. Add MongoDB plugin or set `MONGO_URI` env variable (MongoDB Atlas)
5. Set `PORT=5000` environment variable
6. Done — you get a live URL!

### Environment Variables
```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=personal_finance_db
SECRET_KEY=your-secret-key
DEBUG=false
```

---

## 🎯 Features

| Feature | Description |
|---|---|
| Dashboard | Live stats, charts, recent transactions |
| Add Transaction | Income/Expense with category + date |
| Reports | Monthly summary, category breakdown, trend charts |
| Health Score | 0-100 financial health rating |
| Anomaly Detection | Flags unusually large expenses |
| Savings Forecast | 6-month projection with confidence range |
| Budgets | Set monthly limits with 70/90/100% alerts |
| Goals | Track savings targets with progress bars |

---

## 🛠 Tech Stack

- **Backend**: Python 3 + Flask
- **Database**: MongoDB (pymongo)
- **Charts**: Chart.js (CDN)
- **Icons**: Font Awesome 6
- **Fonts**: DM Sans + Space Mono (Google Fonts)
- **No frontend framework** — pure HTML/CSS/JS
=======
# Personal-Finance-Manager
>>>>>>> e756dc2ba710a11d16d7220c0ad9aa199289db0d
