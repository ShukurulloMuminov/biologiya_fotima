import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, MessageOriginChannel

import database as db
import keyboards as kb
from config import ADMIN_IDS, REQUIRED_REFERRALS

router = Router()


class BroadcastState(StatesGroup):
    waiting_message = State()


class ChannelSetupState(StatesGroup):
    waiting_forward = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("cancel"))
async def cancel_action(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if await state.get_state() is not None:
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=kb.admin_reply_keyboard())
    else:
        await message.answer("Bekor qilinadigan hech narsa yo'q.")


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🛠 Admin panel ochildi. Pastdagi tugmalardan foydalaning:",
        reply_markup=kb.admin_reply_keyboard()
    )


@router.message(F.text == "📊 Statistika")
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    total = await db.count_users()
    await message.answer(f"👥 Jami foydalanuvchilar: {total}")


@router.message(F.text == "🏆 Top referal")
async def admin_top(message: Message):
    if not is_admin(message.from_user.id):
        return
    rows = await db.top_referrers(10)
    if not rows:
        text = "Hozircha ma'lumot yo'q."
    else:
        lines = ["🏆 Eng ko'p referal qilganlar:"]
        for i, r in enumerate(rows, 1):
            name = r["full_name"] or (f"@{r['username']}" if r["username"] else str(r["user_id"]))
            lines.append(f"{i}. {name} — {r['points']} ball")
        text = "\n".join(lines)
    await message.answer(text)


@router.message(F.text == "📢 Xabar yuborish")
async def admin_broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabarni shu yerga yuboring "
        "(matn, rasm, video — barchasi qo'llab-quvvatlanadi).\n\nBekor qilish uchun /cancel"
    )
    await state.set_state(BroadcastState.waiting_message)


@router.message(F.text == "🔗 Yopiq kanalni almashtirish")
async def channel_setup_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    current_title = await db.get_setting("private_channel_title")
    current_line = f"\n\nHozirgi kanal: {current_title}" if current_title else ""
    await message.answer(
        "🔗 Yopiq kanalni almashtirish uchun:\n\n"
        "1️⃣ Avval botni yangi yopiq kanalga ADMIN qilib qo'shing "
        "(\"Havola orqali taklif qilish / Invite Users via Link\" huquqi bilan)\n"
        "2️⃣ So'ngra o'sha kanaldagi istalgan xabarni shu yerga FORWARD qiling"
        f"{current_line}\n\nBekor qilish uchun /cancel"
    )
    await state.set_state(ChannelSetupState.waiting_forward)


@router.message(ChannelSetupState.waiting_forward)
async def channel_setup_receive(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    origin = message.forward_origin
    if not isinstance(origin, MessageOriginChannel):
        await message.answer(
            "❌ Bu kanaldan forward qilingan xabar emas. "
            "Iltimos, yangi yopiq kanaldagi xabarni forward qiling."
        )
        return

    channel = origin.chat
    channel_id = channel.id
    channel_title = channel.title or str(channel_id)

    try:
        bot_id = (await bot.get_me()).id
        bot_member = await bot.get_chat_member(channel_id, bot_id)
    except Exception:
        await message.answer(
            "❌ Bot bu kanalga kira olmadi. Botni administrator sifatida "
            "shu kanalga qo'shganingizga ishonch hosil qiling va qayta urinib ko'ring."
        )
        return

    if bot_member.status != "administrator":
        await message.answer("⚠️ Bot bu kanalda hali administrator emas. Avval admin qilib qo'shing va qayta urinib ko'ring.")
        return

    if not getattr(bot_member, "can_invite_users", False):
        await message.answer(
            "⚠️ Bot administrator, lekin unga \"Invite Users via Link\" huquqi berilmagan. "
            "Iltimos shu huquqni yoqing va qayta urinib ko'ring."
        )
        return

    await db.set_setting("private_channel_id", str(channel_id))
    await db.set_setting("private_channel_title", channel_title)
    await state.clear()

    await message.answer(
        "✅ Yopiq kanal muvaffaqiyatli o'zgartirildi!\n\n"
        f"📌 Nomi: {channel_title}\n"
        f"🆔 ID: {channel_id}\n\n"
        f"Endi {REQUIRED_REFERRALS} ta referal to'lgan foydalanuvchilarga shu kanalga havola yuboriladi."
    )


@router.message(BroadcastState.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    user_ids = await db.get_all_user_ids()
    await message.answer(f"⏳ Xabar {len(user_ids)} ta foydalanuvchiga yuborilmoqda...")

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await message.copy_to(uid)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # flood-limitdan saqlanish uchun kichik pauza

    await message.answer(f"✅ Yuborildi: {sent} ta\n❌ Yuborilmadi: {failed} ta")
