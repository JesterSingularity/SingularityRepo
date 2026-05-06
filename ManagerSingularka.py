from .. import loader, utils
from telethon.tl.types import MessageEntityCustomEmoji
import re


@loader.tds
class ManagerSingularka(loader.Module):
    """Менеджер быстрых шаблонов"""

    strings = {"name": "ManagerSingularka"}

    UPDATE_URL = "https://raw.githubusercontent.com/JesterSingularity/SingularityRepo/main/ManagerSingularka.py"

    async def client_ready(self, client, db):
        self.db = db
        self.templates = self.db.get("ManagerSingularka", "templates", {})

    def save(self):
        self.db.set("ManagerSingularka", "templates", self.templates)

    # =========================
    #         UPDATE
    # =========================
    async def updatemodcmd(self, message):
        await utils.answer(message, "🔄 Обновляю модуль...")

        try:
            await self.allmodules.commands["loadmod"](
                await message.reply(self.UPDATE_URL)
            )
        except Exception as e:
            await utils.answer(message, f"❌ Ошибка:\n{e}")

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
        self.save()

        await utils.answer(message, f"✅ Шаблон {cmd} добавлен")

    async def deltplcmd(self, message):
        cmd = utils.get_args_raw(message).strip()

        if cmd not in self.templates:
            return await utils.answer(message, "❌ Шаблон не найден")

        self.templates.pop(cmd)
        self.save()

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
        self.save()

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
        self.save()

        await utils.answer(message, "😎 Emoji сохранены")

    # =========================
    #        АВТОЗАМЕНА
    # =========================

    @loader.watcher(outgoing=True)
    async def watcher(self, message):
        text = (message.raw_text or "").strip()

        for key, value in self.templates.items():
            if text == key or text.startswith(key + " "):

                if getattr(message, "_tpl_processed", False):
                    return
                message._tpl_processed = True

                final_text, entities = self.insert_premium_emojis(
                    value.get("text", ""),
                    value.get("emoji_ids", [])
                )

                try:
                    await message.edit(final_text, formatting_entities=entities)
                except:
                    await message.edit(final_text)

                return
