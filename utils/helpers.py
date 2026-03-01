def compute_mean(values):
    return sum(values) / len(values) if values else 0.0

def compute_std_dev(values):
    if len(values) < 2:
        return 0.0
    mean = compute_mean(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance ** 0.5

def safe_divide(numerator, denominator, default=0.0):
    return numerator / denominator if denominator else default

def format_currency(amount, symbol="Rs."):
    return f"{symbol}{float(amount):,.2f}"

def format_date(dt):
    return dt.strftime("%d-%b-%Y") if dt else ""

def clear_screen():
    import os
    os.system("cls" if os.name == "nt" else "clear")

def print_table(headers, rows, col_widths=None):
    pass

def month_name(month):
    names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return names[month - 1] if 1 <= month <= 12 else str(month)