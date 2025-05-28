import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

SHEET_NAME='Траты'
SHEET_CATEGORIES_NAME = 'Категории'
TABLE_NAME='Мои траты'

ADMINS_UID = os.getenv('ADMINS_UID')

USER_FILES_JSON = "user_files.json"  # можно указать абсолютный путь, если нужно, иначе лежит там где bot.py

GSCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", GSCOPE)
client = gspread.authorize(creds)