import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

SHEET_NAME='Траты'
SHEET_CATEGORIES_NAME = 'Категории'
TABLE_NAME='Мои траты'

ADMIN_UID = os.getenv('ADMIN_UID')
ADMINS_UID = os.getenv("ADMINS_UID", "").split(",")
DATABASE_URL = os.getenv('DATABASE_URL')
DB_CONFIG = os.getenv('DB_CONFIG')

GSCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = None
try:
    if os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", GSCOPE)
    else:
        raise FileNotFoundError
except Exception as e:
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", GSCOPE)
    except Exception as e2:
        # print("Не удалось загрузить credentials.json ни из корня проекта, ни из /etc/secrets.")
        raise e2
    
client = gspread.authorize(creds)

EMAIL_AGENT = os.getenv('EMAIL_AGENT')
N_ROW_TEXT = 3
N_COLUMN = 4