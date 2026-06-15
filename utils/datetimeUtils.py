from datetime import datetime

def date_to_month_year(date_str: str) -> str:
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.strftime("%B %Y")