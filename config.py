import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Baza (SQLite - o'rnatish talab qilmaydi, oddiy fayl) ---
DB_PATH = os.getenv("DB_PATH", "referral_bot.db")

# --- Majburiy obuna kanali ---
# Username orqali tekshiriladi (bot shu kanalda admin bo'lishi shart)
MANDATORY_CHANNEL_USERNAME = "@fotimaismoilovaattestatsiya"

# --- Yopiq kanal ---
# Telegram Bot API'da kanal/supergruh ID'lari -100 prefiksi bilan ishlatiladi.
# Siz bergan ID: 4488514906 -> to'liq ID: -1004488514906
# Agar xato bo'lsa, README'dagi "Kanal ID'sini tekshirish" bo'limiga qarang.
PRIVATE_CHANNEL_ID = -1004488514906
PRIVATE_CHANNEL_INVITE_LINK = "https://t.me/+voRpLCGdV-U4YWFi"  # agar avtomatik havola yaratib bo'lmasa, shu ishlatiladi

# --- Referal shart ---
REQUIRED_REFERRALS = int(os.getenv("REQUIRED_REFERRALS", "5"))

# --- Adminlar ---
# .env faylida: ADMIN_IDS=123456789,987654321
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
