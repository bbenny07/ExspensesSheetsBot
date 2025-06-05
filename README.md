# Telegram Table Bot 📋

A Telegram bot integrated with Google Sheets that lets users:
- view table rows,
- edit or delete records,
- add new entries with minimal input,
- navigate through records using inline buttons.

## 🚀 Features
- 🔗 Google Sheets integration
- 🔄 Inline navigation (⬅️ ➡️)
- ✏️ Row editing
- 🗑️ Selective deletion
- ➕ Add new records quickly without needing full category/date input
- 🧠 FSM state management (aiogram)

## 📦 Installation

```bash
git clone https://github.com/yourusername/telegram-table-bot.git](https://github.com/bbenny07/ExspensesSheetsBot.git)
cd ExspensesSheetsBot
pip install -r requirements.txt
```
# PostgreSQL Database Setup
This bot requires a PostgreSQL database to store data.
Install PostgreSQL (if not installed) from https://www.postgresql.org/download/.
Create a database and a user with appropriate privileges:
```bash
# Access PostgreSQL shell
psql -U postgres
CREATE DATABASE your_database_name;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
\q
```
# 🛠️ Configuration 
1. Set your Telegram Bot Token, admin UIDs, and database name in the .env file.
   Use the provided .env.example as a template, place .env file in the root directory
2. Place your Google service account credentials file as credentials.json in the root directory.
3. Run the bot:
```bash
python bot.py
```
