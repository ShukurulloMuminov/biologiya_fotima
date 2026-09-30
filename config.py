import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Baza (SQLite - o'rnatish talab qilmaydi, oddiy fayl) ---
DB_PATH = os.getenv("DB_PATH", "referral_bot.db")

# --- Majburiy obuna kanallari ---
# Istalgancha kanal qo'shishingiz mumkin. Bot HAR BIR kanalda admin bo'lishi shart.
#
# chat_id: ochiq kanal uchun "@username", yopiq kanal uchun raqamli ID (-100...)
# title:   tugmada ko'rinadigan nom
# url:     tugma bosilganda ochiladigan havola (ochiq kanal: https://t.me/username,
#          yopiq kanal: invite link)
MANDATORY_CHANNELS = [
    {
        "chat_id": "@fotimaismoilovaattestatsiya",
        "title": "Asosiy kanal",
        "url": "https://t.me/fotimaismoilovaattestatsiya",
    },
    # Yangi kanal qo'shish uchun pastdagi namunani ochib, o'zingiznikini yozing:

    {
         "chat_id": "@Pedagogikmahoratakademiyasi",
         "title": "4-kanal",
         "url": "https://t.me/Pedagogikmahoratakademiyasi",
     },

]

# Eski kod (masalan, handlers/admin.py) shu nomni import qilsa, xato bermasligi uchun qoldirildi.
MANDATORY_CHANNEL_USERNAME = MANDATORY_CHANNELS[0]["chat_id"]

# --- Yopiq kanal ---
# Telegram Bot API'da kanal/supergruh ID'lari -100 prefiksi bilan ishlatiladi.
# Siz bergan ID: 4488514906 -> to'liq ID: -1004488514906
# Agar xato bo'lsa, README'dagi "Kanal ID'sini tekshirish" bo'limiga qarang.
PRIVATE_CHANNEL_ID = -1004488514906
PRIVATE_CHANNEL_INVITE_LINK = "https://t.me/+voRpLCGdV-U4YWFi"  # agar avtomatik havola yaratib bo'lmasa, shu ishlatiladi

# --- Referal shart ---
REQUIRED_REFERRALS = int(os.getenv("REQUIRED_REFERRALS", "3"))

# --- Adminlar ---
# .env faylida: ADMIN_IDS=123456789,987654321
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]