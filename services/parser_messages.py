from datetime import datetime, timedelta
import re

def parse_message(msg_text: str, msg_date: datetime):
    parts = msg_text.strip().split()

    try:
        if re.match(r'^\d{1,2}\.\d{1,2}$', parts[0]):
            day, month = map(int, parts[0].split('.'))
            date = datetime(msg_date.year, month, day).date()
            category = parts[1].capitalize()
            amount = float(parts[2].replace(',', '.'))
            comment = " ".join(parts[3:])
        elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{2,4}$', parts[0]):
            day, month, year = map(int, parts[0].split('.'))
            year = 2000 + year%100
            date = datetime(year, month, day).date()
            category = parts[1].capitalize()
            amount = float(parts[2].replace(',', '.'))
            comment = " ".join(parts[3:])
        elif re.match(r'^-?\d+$', parts[0]):
            offset = int(parts[0])
            date = (msg_date + timedelta(days=offset)).date()
            category = parts[1].capitalize()
            amount = float(parts[2].replace(',', '.'))
            comment = " ".join(parts[3:])
        else:
            date = msg_date.date()
            category = parts[0].capitalize()
            amount = float(parts[1].replace(',', '.'))
            comment = " ".join(parts[2:])
    except Exception:
        return None

    return date.strftime('%d.%m.%Y'), category, amount, comment
