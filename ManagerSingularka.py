from .. import loader, utils
from telethon.tl.types import MessageEntityCustomEmoji
import re
import json
import os
import requests


@loader.tds
class ManagerSingularka(loader.Module):
    """Менеджер быстрых шаблонов"""

    strings = {"name": "ManagerSingularka"}

    BASE_DIR = os.path.dirname(__file__)
    FILE = os.path.join(BASE_DIR, "templates.json")

    # 🔗 ВСТАВЬ СЮДА СВОЮ RAW ССЫЛКУ
    UPDATE_URL = "https://raw.githubusercontent.com/USER/REPO/main/ManagerSingularka.py"

    # =========================
    #        ЗАГРУЗКА
    # =========================
    def load_templates(self):
        if not os.path.exists(self.FILE):
            return {}

        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_templates(self):
        try:
            with open(self.FILE, "w", encoding="utf-8") as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    async def client_ready(self, client, db):
        self.templates = self.load_templates()

    # =========================
    #     UPDATE КОМАНДА
    # =========================
    async def updatecmd(self, message):
        """Обновить модуль"""
        await utils.answer(message, "🔄 Обновляю модуль...")

        try:
            r = requests.get(self.UPDATE_URL)
            if r.status_code != 200:
                return await utils.answer(message, "❌ Не удалось скачать обновление")

            code = r.text

            path = os.path.abspath(__file__)

            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            await utils.answer(message, "✅ Обновлено! Перезагружаю...")

            # перезагрузка модуля
            await self.reload()

        except Exception as e:
            await utils.answer(message, f"❌ Ошибка:\n{e}")

    async def reload(self):
        """Перезагрузка модуля"""
        try:
            from .. import loader
            loader.reload_modules()
        except:
            pass

    # =========================
    #     PREMIUM EMOJI
    # =========================
    def insert_premium_emojis(self, text, emoji_ids):
        entities = []
        pattern = r":(\d+):"
        matches = list(re.finditer(pattern, text))

        shift = 0

        for m in matches:
            i = int(m.group(1)) - 1
            if i >= len(emoji_ids):
                continue

            emoji_id = int(emoji_ids[i])

            start = m.start() - shift
            end = m.end() - shift

            text = text[:start] + "□️" + text[end:]

            entities.append(
                MessageEntityCustomEmoji(
                    offset=start,
                    length=1,
                    document_id=emoji_id
                )
            )

            shift += (end - start - 1)

        return text, entities

    # =========================
    #         КОМАНДЫ
    # =========================

    async def addtplcmd(self, message):
        args = utils.get_args_raw(message)

        if "|" not in args:
            return await utils.answer(message, "❌ Формат: .addtpl .cmd | текст")

        cmd, text = args.split("|", 1)
        cmd = cmd.strip()
        text = text.strip()

        self.templates[cmd] = {"text": text, "emoji_ids": []}
        self.save_templates()

        await utils.answer(message, f"✅ Шаблон {cmd} добавлен")

    async def deltplcmd(self, message):
        cmd = utils.get_args_raw(message).strip()

        if cmd not in self.templates:
            return await utils.answer(message, "❌ Шаблон не найден")

        self.templates.pop(cmd)
        self.save_templates()

        await utils.answer(message, f"🗑 Удалён {cmd}")

    async def listtplcmd(self, message):
        if not self.templates:
            return await utils.answer(message, "📭 Шаблонов нет")

        text = "📚 Шаблоны:\n\n"
        for k in self.templates:
            text += f"• {k}\n"

        await utils.answer(message, text)

    async def edittplcmd(self, message):
        args = utils.get_args_raw(message)

        if "|" not in args:
            return await utils.answer(message, "❌ Формат: .edittpl .cmd | текст")

        cmd, text = args.split("|", 1)
        cmd = cmd.strip()
        text = text.strip()

        if cmd not in self.templates:
            return await utils.answer(message, "❌ Шаблон не найден")

        self.templates[cmd]["text"] = text
        self.save_templates()

        await utils.answer(message, f"✏️ Обновлён {cmd}")

    async def setemojicmd(self, message):
        cmd = utils.get_args_raw(message).strip()

        if cmd not in self.templates:
            return await utils.answer(message, "❌ Шаблон не найден")

        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, "❌ Ответь на сообщение с emoji")

        ids = []
        if reply.entities:
            for e in reply.entities:
                if isinstance(e, MessageEntityCustomEmoji):
                    ids.append(e.document_id)

        if not ids:
            return await utils.answer(message, "❌ Нет premium emoji")

        self.templates[cmd]["emoji_ids"] = ids
        self.save_templates()

        await utils.answer(message, "😎 Emoji сохранены")

    # =========================
    #        АВТОЗАМЕНА
    # =========================

    @loader.watcher(outgoing=True)
    async def watcher(self, message):
        text = (message.raw_text or "").strip()

        for key, value in self.templates.items():
            if text == key or text.startswith(key + " "):
                final_text, entities = self.insert_premium_emojis(
                    value.get("text", ""),
                    value.get("emoji_ids", [])
                )

                try:
                    await message.edit(final_text, formatting_entities=entities)
                except:
                    await message.edit(final_text)

                return
