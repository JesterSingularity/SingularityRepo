# -*- coding: utf-8 -*-

import os
from aiogram import Bot, Dispatcher, executor, types

TOKEN = os.getenv("BOT_TOKEN")

# ID группы
GROUP_ID = -1003709910240

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

user_data = {}

# =========================
# КНОПКИ
# =========================

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

btn1 = types.KeyboardButton("💰 Скупка")
btn2 = types.KeyboardButton("🔄 Обмен между участниками")
btn3 = types.KeyboardButton("📜 Порядок сделки")

kb.add(btn1)
kb.add(btn2)
kb.add(btn3)

# =========================
# START
# =========================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    text = """
<b>Добро пожаловать в astervex ♡</b>

Через этого бота вы можете оставить заявку на проведение безопасной сделки.
"""

    await message.answer(text, reply_markup=kb)

# =========================
# ПРАВИЛА
# =========================

@dp.message_handler(lambda message: message.text == "📜 Порядок сделки")
async def rules(message: types.Message):

    text = """
<b>✧ порядок проведения сделки ✧</b>

1. Оставьте заявку через нашего бота.

• Если это скупка — укажите:
<code>@юзернейм гаранта</code>

• Если это обмен между участниками — укажите:
<code>@юзернейм гаранта</code>
<code>@юзернейм второго участника сделки</code>

2. После принятия заявки:

— при скупке сделка проводится в личных сообщениях  
— при обмене создаётся общая группа со всеми участниками

3. Гарант сопровождает сделку до её полного завершения.

4. После окончания сделки не забудьте оставить отзыв.

Спасибо, что выбираете <b>astervex ♡</b>
"""

    await message.answer(text)

# =========================
# СКУПКА
# =========================

@dp.message_handler(lambda message: message.text == "💰 Скупка")
async def buy_start(message: types.Message):

    user_data[message.from_user.id] = {
        "deal_type": "Скупка"
    }

    await message.answer("Введите @юзернейм гаранта:")

    dp.register_message_handler(
        process_guarantor_buy,
        state="*"
    )

async def process_guarantor_buy(message: types.Message):

    if message.from_user.id not in user_data:
        return

    if user_data[message.from_user.id].get("deal_type") != "Скупка":
        return

    guarantor = message.text

    username = message.from_user.username
    user_id = message.from_user.id

    text = f"""
<b>Новая заявка на скупку</b>

👤 Пользователь: @{username}
🆔 ID: <code>{user_id}</code>

🛡 Гарант: {guarantor}
"""

    await bot.send_message(GROUP_ID, text)

    await message.answer(
        "✅ Ваша заявка отправлена администрации."
    )

    del user_data[message.from_user.id]

# =========================
# ОБМЕН
# =========================

@dp.message_handler(lambda message: message.text == "🔄 Обмен между участниками")
async def exchange_start(message: types.Message):

    user_data[message.from_user.id] = {
        "deal_type": "Обмен"
    }

    await message.answer("Введите @юзернейм гаранта:")

    dp.register_message_handler(
        process_exchange_guarantor,
        state="*"
    )

async def process_exchange_guarantor(message: types.Message):

    if message.from_user.id not in user_data:
        return

    if user_data[message.from_user.id].get("deal_type") != "Обмен":
        return

    user_data[message.from_user.id]["guarantor"] = message.text

    await message.answer(
        "Введите @юзернейм второго участника:"
    )

    dp.register_message_handler(
        process_exchange_user,
        state="*"
    )

async def process_exchange_user(message: types.Message):

    if message.from_user.id not in user_data:
        return

    guarantor = user_data[message.from_user.id]["guarantor"]
    second_user = message.text

    username = message.from_user.username
    user_id = message.from_user.id

    text = f"""
<b>Новая заявка на обмен</b>

👤 Пользователь: @{username}
🆔 ID: <code>{user_id}</code>

🛡 Гарант: {guarantor}
👥 Второй участник: {second_user}
"""

    await bot.send_message(GROUP_ID, text)

    await message.answer(
        "✅ Ваша заявка отправлена администрации."
    )

    del user_data[message.from_user.id]

# =========================
# RUN
# =========================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
