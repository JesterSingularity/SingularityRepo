# -*- coding: utf-8 -*-

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, executor, types

# =====================================
# TOKEN
# =====================================

TOKEN = os.getenv("BOT_TOKEN")

# ID группы куда будут приходить анкеты
GROUP_ID = -1003709910240

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# =====================================
# ХРАНЕНИЕ ДАННЫХ
# =====================================

user_data = {}

questions = [
    "1️⃣ Какой ваш опыт?",
    "2️⃣ Сколько времени уделишь проекту?",
    "3️⃣ Согласен отдавать 25% админу?",
    "4️⃣ Готов делать 5 отзывов в день?",
    "5️⃣ Есть личные отзывы?",
    "6️⃣ Понимаешь, что вранье админам ни к чему хорошему не приведет?",
    "7️⃣ Готов сразу начать плотную работу на повышение?"
]

# =====================================
# START
# =====================================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn = types.KeyboardButton("📋 Заполнить анкету")

    kb.add(btn)

    text = """
<b>Добро пожаловать.</b>

Для вступления в команду заполните анкету.
"""

    await message.answer(text, reply_markup=kb)

# =====================================
# НАЧАЛО АНКЕТЫ
# =====================================

@dp.message_handler(lambda message: message.text == "📋 Заполнить анкету")
async def form_start(message: types.Message):

    user_data[message.from_user.id] = {
        "step": 0,
        "answers": []
    }

    await message.answer(questions[0])

# =====================================
# ОБРАБОТКА ОТВЕТОВ
# =====================================

@dp.message_handler(lambda message: message.from_user.id in user_data)
async def process_form(message: types.Message):

    user_id = message.from_user.id

    data = user_data[user_id]

    data["answers"].append(message.text)

    data["step"] += 1

    # Если еще есть вопросы
    if data["step"] < len(questions):

        await message.answer(
            questions[data["step"]]
        )

    # Если анкета закончена
    else:

        username = message.from_user.username or "без_username"

        answers = data["answers"]

        text = f"""
<b>Новая анкета</b>

👤 Пользователь: @{username}
🆔 ID: <code>{user_id}</code>

<b>Ответы:</b>

1️⃣ Опыт:
{answers[0]}

2️⃣ Время проекту:
{answers[1]}

3️⃣ 25% админу:
{answers[2]}

4️⃣ 5 отзывов в день:
{answers[3]}

5️⃣ Личные отзывы:
{answers[4]}

6️⃣ Отношение ко вранью:
{answers[5]}

7️⃣ Готовность к работе:
{answers[6]}
"""

        await bot.send_message(GROUP_ID, text)

        await message.answer(
            "✅ Анкета отправлена администрации."
        )

        del user_data[user_id]

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

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    server.serve_forever()

# =====================================
# RUN
# =====================================

if __name__ == "__main__":

    threading.Thread(target=run_web).start()

    executor.start_polling(dp, skip_updates=True)
