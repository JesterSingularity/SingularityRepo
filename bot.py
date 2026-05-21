# -*- coding: utf-8 -*-
# pip install aiogram==2.25.2

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
<b>Добро пожаловать в ᥲ᥉tᥱr᥎ᥱⲭ ♡</b>

Через этого бота вы можете оставить заявку на проведение безопасной сделки.
"""

    await message.answer(text, reply_markup=kb)

# =========================
# ПРАВИЛА
# =========================

@dp.message_handler(lambda message: message.text == "📜 Порядок сделки")
async def rules(message: types.Message):

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

@dp.message_handler(lambda message: message.text == "💰 Скупка")
async def buyout(message: types.Message):

    user_data[message.from_user.id] = "buy"

    await message.answer(
        "Введите @юзернейм гаранта:"
    )

# =========================
# ОБМЕН
# =========================

@dp.message_handler(lambda message: message.text == "🔄 Обмен между участниками")
async def exchange(message: types.Message):

    user_data[message.from_user.id] = "exchange"

    await message.answer(
        "Введите данные в формате:\n\n"
        "@гарант\n"
        "@второй_участник"
    )

# =========================
# ОБРАБОТКА
# =========================

@dp.message_handler()
async def forms(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_data:
        return

    deal_type = user_data[user_id]

    # =========================
    # СКУПКА
    # =========================

    if deal_type == "buy":

        guarantor = message.text

        text = f"""
<b>📥 Новая заявка</b>

<b>Тип:</b> Скупка

<b>Пользователь:</b>
@{message.from_user.username}

<b>ID:</b>
<code>{message.from_user.id}</code>

<b>Гарант:</b>
{guarantor}
"""

        await bot.send_message(GROUP_ID, text)

        await message.answer(
            "✅ Заявка отправлена."
        )

        del user_data[user_id]

    # =========================
    # ОБМЕН
    # =========================

    elif deal_type == "exchange":

        lines = message.text.splitlines()

        if len(lines) < 2:

            await message.answer(
                "❌ Неверный формат.\n\n"
                "@гарант\n"
                "@второй_участник"
            )

            return

        guarantor = lines[0]
        second_user = lines[1]

        text = f"""
<b>📥 Новая заявка</b>

<b>Тип:</b> Обмен

<b>Создатель:</b>
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
            "✅ Заявка на обмен отправлена."
        )

        del user_data[user_id]

# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    print("Бот запущен")
    executor.start_polling(dp, skip_updates=True)    if deal_type == "Скупка":

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
