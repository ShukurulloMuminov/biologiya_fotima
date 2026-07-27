# Referal Telegram Bot

Foydalanuvchi 5 ta do'stini taklif qilsa, bot avtomatik ravishda yopiq kanalga
bir martalik kirish havolasini yuboradi. Majburiy obuna tekshiruvi va
admin panel (statistika + barcha foydalanuvchilarga xabar yuborish +
yopiq kanalni botdan turib almashtirish) mavjud.

Baza sifatida **SQLite** ishlatiladi — alohida server yoki sudo/admin
huquqi kerak emas, oddiy fayl sifatida ishlaydi.

## 1. Talablar

- Python 3.10+
- (PostgreSQL yoki boshqa alohida baza kerak EMAS)

## 2. O'rnatish

```bash
cd referral_bot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. .env faylini sozlash

`.env.example` faylini nusxalab `.env` nomida saqlang va to'ldiring:

```bash
cp .env.example .env
nano .env
```

- `BOT_TOKEN` — BotFather'dan olgan **to'liq** tokeningizni kiriting
- `DB_PATH` — SQLite fayl nomi (o'zgartirish shart emas, standart holicha qoldiring)
- `ADMIN_IDS` — o'zingizning Telegram ID'ingiz (bilmasangiz @userinfobot ga yozing)

## 4. Botni ikkala kanalga ADMIN qilib qo'shish — MUHIM!

- **Majburiy kanal** (`@fotimaismoilovaattestatsiya`) — botni admin qiling
  (obunani tekshirish uchun shart)
- **Yopiq kanal** — botni admin qiling va **"Invite Users via Link"**
  huquqini bering (avtomatik bir martalik havola yaratish uchun shart).
  Kanalni bot ichidan ham almashtirish mumkin — pastdagi "Foydalanish" bo'limiga qarang.

## 5. Botni ishga tushirish

```bash
python main.py
```

Ishga tushganda joriy papkada `referral_bot.db` fayli avtomatik yaratiladi —
bu sizning butun bazangiz. Uni zaxira nusxalash uchun shu faylni ko'chirsa bo'ldi.

## 6. Serverda doimiy ishlashi uchun (systemd)

Agar sizda sudo bo'lsa, `/etc/systemd/system/referralbot.service` yarating:

```ini
[Unit]
Description=Referral Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/referral_bot
ExecStart=/home/YOUR_USERNAME/referral_bot/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable referralbot
sudo systemctl start referralbot
```

**Sudo yo'q bo'lsa** — `tmux` yoki `screen` ishlatib fonda qoldirish mumkin:

```bash
tmux new -s referralbot
source venv/bin/activate
python main.py
```
Keyin `Ctrl+B`, so'ng `D` bosib chiqing (bot ishlashda davom etadi).
Qaytib kirish uchun: `tmux attach -t referralbot`

## 7. Foydalanish

- Foydalanuvchi: `/start` — obunani tekshiradi, referal havola beradi
- Admin: `/start` yoki `/admin` — pastda admin menyusi chiqadi:
  - **📊 Statistika** — jami foydalanuvchilar soni
  - **🏆 Top referal** — eng ko'p taklif qilganlar
  - **📢 Xabar yuborish** — barcha foydalanuvchilarga xabar (matn/rasm/video)
  - **🔗 Yopiq kanalni almashtirish** — yopiq kanalni kod yozmasdan, botdan turib o'zgartirish:
    1. Botni yangi yopiq kanalga admin qilib qo'shing ("Invite Users via Link" huquqi bilan)
    2. Shu tugmani bosing
    3. Yangi kanaldagi istalgan xabarni botga forward qiling
    4. Bot avtomatik tekshirib, yangi kanalni saqlaydi
  - `/cancel` — istalgan jarayonni (broadcast, kanal almashtirish) bekor qiladi

## 8. Adminni boshqa odamga o'tkazish

`.env` faylni oching:

```bash
nano .env
```

`ADMIN_IDS=` qatorini yangi odamning Telegram ID'siga almashtiring, saqlang,
so'ng botni qayta ishga tushiring.

## Loyiha tuzilishi

```
referral_bot/
├── main.py              # ishga tushirish
├── config.py            # sozlamalar (.env dan o'qiydi)
├── database.py          # SQLite bilan ishlash
├── keyboards.py         # tugmalar
├── handlers/
│   ├── user.py          # /start, obuna tekshirish, referal logikasi
│   └── admin.py         # /admin, statistika, broadcast, kanal sozlash
├── requirements.txt
├── .env.example
└── referral_bot.db      # (avtomatik yaratiladi, bazangiz shu yerda)
```

## Qo'shimcha g'oyalar (xohlasangiz qo'shib beraman)

- Referal darajalari (masalan 5 ta = 1-kanal, 15 ta = 2-kanal/bonus)
- Foydalanuvchilarni Excel (.xlsx) formatda eksport qilish
- Kunlik/haftalik statistika grafigi
- Bir nechta majburiy kanal qo'llab-quvvatlash
- Referalni firibgarlikdan himoya qilish (bir xil qurilma/IP tekshiruvi)
