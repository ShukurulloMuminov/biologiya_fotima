import asyncio
import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from config import (
    MANDATORY_CHANNELS, PRIVATE_CHANNEL_ID, PRIVATE_CHANNEL_INVITE_LINK,
    REQUIRED_REFERRALS, ADMIN_IDS
)

router = Router()
logger = logging.getLogger(__name__)


async def _is_member(bot: Bot, chat_id, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status not in ("left", "kicked")
    except Exception as e:
        # Bot kanalda admin emas yoki chat_id noto'g'ri bo'lishi mumkin
        logger.warning("get_chat_member xatosi (chat_id=%s): %s", chat_id, e)
        return False


async def get_unsubscribed_channels(bot: Bot, user_id: int) -> list[dict]:
    """Foydalanuvchi hali a'zo bo'lmagan majburiy kanallar ro'yxati."""
    results = await asyncio.gather(
        *(_is_member(bot, ch["chat_id"], user_id) for ch in MANDATORY_CHANNELS)
    )
    return [ch for ch, ok in zip(MANDATORY_CHANNELS, results) if not ok]


async def get_private_channel_id() -> int:
    saved = await db.get_setting("private_channel_id")
    if saved:
        return int(saved)
    return PRIVATE_CHANNEL_ID


async def grant_access_if_ready(bot: Bot, user_id: int):
    user = await db.get_user(user_id)
    if user and user["points"] >= REQUIRED_REFERRALS and not user["access_granted"]:
        channel_id = await get_private_channel_id()
        try:
            invite = await bot.create_chat_invite_link(
                channel_id, member_limit=1, name=f"ref_{user_id}"
            )
            link = invite.invite_link
        except Exception:
            link = PRIVATE_CHANNEL_INVITE_LINK
        await db.set_access_granted(user_id)
        await bot.send_message(
            user_id,
            f"🎉 Tabriklaymiz! Siz {REQUIRED_REFERRALS} ta biolog tanishingizni taklif qildingiz.\n\n"
            f"Yopiq kanalga kirish uchun havola:\n{link}"
        )


async def process_subscription_confirmed(bot: Bot, user_id: int):
    """Foydalanuvchi obunasi tasdiqlanganda ishga tushadi - referal ballni FAQAT BIR MARTA hisoblaydi."""
    user = await db.get_user(user_id)
    if user and user["referrer_id"] and not user["referral_counted"]:
        referrer_id = user["referrer_id"]
        if await db.user_exists(referrer_id):
            await db.mark_referral_counted(user_id)
            new_points = await db.add_point(referrer_id)
            try:
                await bot.send_message(
                    referrer_id,
                    f"🎉 Sizga yangi referal qo'shildi! Hozirgi ballaringiz: {new_points}/{REQUIRED_REFERRALS}"
                )
            except Exception:
                pass
            await grant_access_if_ready(bot, referrer_id)


async def show_profile(message: Message, bot: Bot, user_id: int):
    user = await db.get_user(user_id)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    text = (
        "👋 Xush kelibsiz!\n\n"
        f"🔗 Sizning referal havolangiz:\n{ref_link}\n\n"
        f"📊 Taklif qilganlaringiz: {user['points']}/{REQUIRED_REFERRALS}\n\n"
        f"{REQUIRED_REFERRALS} ta biolog tanishingizni ushbu havola orqali taklif qilsangiz, "
        "yopiq kanalga kirish havolasini olasiz."
    )
    await message.answer(text, reply_markup=kb.profile_keyboard(ref_link))


@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject, bot: Bot):
    user_id = message.from_user.id
    referrer_id = None
    if command.args and command.args.isdigit():
        ref_id = int(command.args)
        if ref_id != user_id:
            referrer_id = ref_id

    if not await db.user_exists(user_id):
        await db.add_user(user_id, message.from_user.username, message.from_user.full_name, referrer_id)

    missing = await get_unsubscribed_channels(bot, user_id)
    if missing:
        await message.answer(
            "Botdan foydalanish uchun avval quyidagi kanallarga a'zo bo'ling, "
            "so'ng \"✅ Tekshirish\" tugmasini bosing:",
            reply_markup=kb.subscribe_keyboard(missing)
        )
        return

    await process_subscription_confirmed(bot, user_id)
    await show_profile(message, bot, user_id)

    if user_id in ADMIN_IDS:
        await message.answer(
            "🛠 Siz admin sifatida ro'yxatdan o'tgansiz. Pastdagi menyudan foydalaning:",
            reply_markup=kb.admin_reply_keyboard()
        )


@router.callback_query(F.data == "check_sub")
async def check_sub_handler(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    missing = await get_unsubscribed_channels(bot, user_id)
    if not missing:
        await callback.message.delete()
        await process_subscription_confirmed(bot, user_id)
        await show_profile(callback.message, bot, user_id)
        if user_id in ADMIN_IDS:
            await callback.message.answer(
                "🛠 Siz admin sifatida ro'yxatdan o'tgansiz. Pastdagi menyudan foydalaning:",
                reply_markup=kb.admin_reply_keyboard()
            )
    else:
        names = ", ".join(ch["title"] for ch in missing)
        await callback.answer(f"❌ Hali a'zo bo'lmagansiz: {names}", show_alert=True)
        try:
            await callback.message.edit_reply_markup(
                reply_markup=kb.subscribe_keyboard(missing)
            )
        except Exception:
            # Ro'yxat o'zgarmagan bo'lsa Telegram "message is not modified" xatosini beradi
            pass


@router.callback_query(F.data == "my_stats")
async def my_stats_handler(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    await callback.answer(
        f"Ballaringiz: {user['points']}/{REQUIRED_REFERRALS}",
        show_alert=True
    )