# -*- coding: utf-8 -*-
# pip install aiogram==3.7.0

import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.client.default import DefaultBotProperties

# =========================
# НАСТРОЙКИ
# =========================

TOKEN = os.getenv("BOT_TOKEN")

# ID ГРУППЫ ДЛЯ ОТПРАВКИ АНКЕТ
GROUP_ID = -1003709910240

# =========================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# Временное хранение заявок
user_data = {}

# Клавиатура
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Скупка")],
        [KeyboardButton(text="🔄 Обмен между участниками")],
        [KeyboardButton(text="📜 Порядок сделки")]
    ],
    resize_keyboard=True
)


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):
    text = """
<b>Добро пожаловать в ᥲ᥉tᥱr᥎ᥱⲭ ♡</b>

Через этого бота вы можете оставить заявку на проведение безопасной сделки.
"""

    await message.answer(text, reply_markup=menu)


# =========================
# ПРАВИЛА
# =========================

@dp.message(F.text == "📜 Порядок сделки")
async def rules(message: Message):
    text = """
<b>⟡ порядок проведения сделки ⟡</b>

1. Оставьте заявку через нашего бота.

• Если это скупка — укажите:
<code>@юзернейм гаранта</code>

• Если это обмен между участниками — укажите:
<code>@юзернейм гаранта</code>
<code>@юзернейм второго участника сделки</code>

2. После принятия заявки:

— при скупке сделка проводится в личных сообщениях
— при обмене создаётся общая группа со всеми участниками

3. Гарант сопровождает сделку до её полного завершения и следит за безопасностью обеих сторон.

4. После окончания сделки не забудьте оставить отзыв — это помогает развивать репутацию проекта и повышает доверие внутри комьюнити.

Спасибо, что выбираете <b>ᥲ᥉tᥱr᥎ᥱⲭ ♡</b>
"""

    await message.answer(text)


# =========================
# СКУПКА
# =========================

@dp.message(F.text == "💰 Скупка")
async def buyout(message: Message):

    user_data[message.from_user.id] = {
        "type": "Скупка"
    }

    await message.answer(
        "Введите @юзернейм гаранта:"
    )


# =========================
# ОБМЕН
# =========================

@dp.message(F.text == "🔄 Обмен между участниками")
async def exchange(message: Message):

    user_data[message.from_user.id] = {
        "type": "Обмен"
    }

    await message.answer(
        "Введите данные в формате:\n\n"
        "@гарант\n"
        "@второй_участник"
    )


# =========================
# ОБРАБОТКА АНКЕТ
# =========================

@dp.message()
async def forms(message: Message):

    user_id = message.from_user.id

    if user_id not in user_data:
        return

    deal_type = user_data[user_id]["type"]

    # =========================
    # СКУПКА
    # =========================

    if deal_type == "Скупка":

        guarantor = message.text.strip()

        text = f"""
<b>📥 Новая заявка</b>

<b>Тип сделки:</b> Скупка

<b>Пользователь:</b>
@{message.from_user.username}

<b>ID:</b>
<code>{message.from_user.id}</code>

<b>Гарант:</b>
{guarantor}
"""

        await bot.send_message(GROUP_ID, text)

        await message.answer(
            "✅ Ваша заявка успешно отправлена.\n\n"
            "Ожидайте ответа гаранта."
        )

        del user_data[user_id]

    # =========================
    # ОБМЕН
    # =========================

    elif deal_type == "Обмен":

        lines = message.text.splitlines()

        if len(lines) < 2:
            await message.answer(
                "❌ Неверный формат.\n\n"
                "Введите:\n"
                "@гарант\n"
                "@второй_участник"
            )
            return

        guarantor = lines[0].strip()
        second_user = lines[1].strip()

        text = f"""
<b>📥 Новая заявка</b>

<b>Тип сделки:</b> Обмен

<b>Создатель заявки:</b>
@{message.from_user.username}

<b>ID:</b>
<code>{message.from_user.id}</code>

<b>Второй участник:</b>
{second_user}

<b>Гарант:</b>
{guarantor}
"""

        await bot.send_message(GROUP_ID, text)

        await message.answer(
            "✅ Заявка на обмен отправлена.\n\n"
            "После принятия сделки будет создана общая группа."
        )

        del user_data[user_id]


# =========================
# ЗАПУСК БОТА
# =========================

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
