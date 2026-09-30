from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def subscribe_keyboard(channels: list[dict]):
    """Faqat hali a'zo bo'linmagan kanallar uchun tugmalar chiqadi."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(text=f"📢 {ch['title']}", url=ch["url"])
    builder.button(text="✅ Tekshirish", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()


def profile_keyboard(referral_link: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Referal havolamni ulashish", url=f"https://t.me/share/url?url={referral_link}")
    builder.button(text="📊 Statistikam", callback_data="my_stats")
    builder.adjust(1)
    return builder.as_markup()


def admin_reply_keyboard():
    """Admin uchun pastda doimiy ko'rinib turadigan menyu tugmalari."""
    builder = ReplyKeyboardBuilder()
    builder.button(text="📊 Statistika")
    builder.button(text="🏆 Top referal")
    builder.button(text="📢 Xabar yuborish")
    builder.button(text="🔗 Yopiq kanalni almashtirish")
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True, is_persistent=True)