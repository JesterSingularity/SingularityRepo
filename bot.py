# -*- coding: utf-8 -*-

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, executor, types

# =====================================
# TOKEN
# =====================================

TOKEN = os.getenv("BOT_TOKEN")

# ID группы
GROUP_ID = -1003709910240

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

user_data = {}

# =====================================
# КНОПКИ
# =====================================

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

btn1 = types.KeyboardButton("💰 Скупка")
btn2 = types.KeyboardButton("🔄 Обмен между участниками")
btn3 = types.KeyboardButton("📜 Порядок сделки")

kb.add(btn1)
kb.add(btn2)
kb.add(btn3)

# =====================================
# START
# =====================================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    text = """
<b>Добро пожаловать в astervex ♡</b>

Через этого бота вы можете оставить заявку на проведение безопасной сделки.
"""

    await message.answer(text, reply_markup=kb)

# =====================================
# ПРАВИЛА
# =====================================

@dp.message_handler(lambda message: message.text == "📜 Порядок сделки")
async def rules(message: types.Message):

    text = """
<b>✧ порядок проведения сделки ✧</b>

1. Оставьте заявку через нашего бота.

• Если это скупка — укажите:
<code>@юзернейм гаранта\n(тот от кого вы перешли в бота)</code>

• Если это обмен между участниками — укажите:
<code>@юзернейм гаранта\n(тот от кого вы перешли в бота)</code>
<code>@юзернейм второго участника сделки</code>

2. После принятия заявки:

— при скупке сделка проводится в личных сообщениях  
— при обмене создаётся общая группа со всеми участниками

3. Гарант сопровождает сделку до её полного завершения.

4. После окончания сделки не забудьте оставить отзыв.

Спасибо, что выбираете <b>astervex ♡</b>
"""

    await message.answer(text)

# =====================================
# СКУПКА
# =====================================

@dp.message_handler(lambda message: message.text == "💰 Скупка")
async def buy_start(message: types.Message):

    user_data[message.from_user.id] = {
        "deal_type": "Скупка"
    }

    await message.answer("Введите @юзернейм гаранта(от кого вы перешли в бота):")

@dp.message_handler(lambda message:
    message.from_user.id in user_data and
    user_data[message.from_user.id]["deal_type"] == "Скупка" and
    "guarantor" not in user_data[message.from_user.id]
)
async def process_buy(message: types.Message):

    guarantor = message.text

    username = message.from_user.username or "без_username"
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

# =====================================
# ОБМЕН
# =====================================

@dp.message_handler(lambda message: message.text == "🔄 Обмен между участниками")
async def exchange_start(message: types.Message):

    user_data[message.from_user.id] = {
        "deal_type": "Обмен"
    }

    await message.answer("Введите @юзернейм гаранта(от кого вы перешли в бота):")

@dp.message_handler(lambda message:
    message.from_user.id in user_data and
    user_data[message.from_user.id]["deal_type"] == "Обмен" and
    "guarantor" not in user_data[message.from_user.id]
)
async def process_exchange_guarantor(message: types.Message):

    user_data[message.from_user.id]["guarantor"] = message.text

    await message.answer(
        "Введите @юзернейм второго участника:"
    )

@dp.message_handler(lambda message:
    message.from_user.id in user_data and
    user_data[message.from_user.id]["deal_type"] == "Обмен" and
    "guarantor" in user_data[message.from_user.id]
)
async def process_exchange_user(message: types.Message):

    guarantor = user_data[message.from_user.id]["guarantor"]
    second_user = message.text

    username = message.from_user.username or "без_username"
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
        "✅ Ваша заявка отправлена администрации.\nОжидайте ответа гаранта"
    )

    del user_data[message.from_user.id]

# =====================================
# FAKE WEB SERVER FOR RENDER
# =====================================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# =====================================
# RUN
# =====================================

if __name__ == "__main__":

    threading.Thread(target=run_web).start()

    executor.start_polling(dp, skip_updates=True)
