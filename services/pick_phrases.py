import random
from statistics import mean
from datetime import datetime, timedelta
from lexicon import categories
EXPENSE_PRAISE_THRESHOLD = 5
EXPENSE_WARNING_THRESHOLD = 40
EXPENSE_CRITICAL_THRESHOLD = 80

def pick_phrase(date_str, category, amount, comment, table):
    if "такси" in [category.lower(), comment.lower()]:
        phrase = random.choice(categories.SUPPORT_PHRASES["taxi_expense"])
    elif "футбол" in [category.lower(), comment.lower()]:
        phrase = random.choice(categories.SUPPORT_PHRASES["football_game_expense"])
    elif "кафе" in [category.lower(), comment.lower()]:
        phrase = random.choice(categories.SUPPORT_PHRASES["cafe_expense"])
    elif amount <= EXPENSE_PRAISE_THRESHOLD:
        phrase = random.choice(categories.SUPPORT_PHRASES["small_expense"])
    elif EXPENSE_WARNING_THRESHOLD <= amount <= EXPENSE_CRITICAL_THRESHOLD:
        phrase = random.choice(categories.SUPPORT_PHRASES["warning_expense"])
    elif amount > EXPENSE_CRITICAL_THRESHOLD:
        phrase = random.choice(categories.SUPPORT_PHRASES["critical_expense"])
    else:
        phrase = random.choice(categories.SUPPORT_PHRASES["normal"])
    return phrase
    