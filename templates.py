# ayu name: Templates
# ayu desc: Менеджер быстрых шаблонов сообщений
# ayu author: JesterSingularity
# ayu version: 1.0.1
# ayu icon: https://raw.githubusercontent.com/JesterSingularity/SingularityRepo/refs/heads/main/imgonline-com-ua-Resize-uqmkQQM094qmw.jpg

# meta developer: @JesterSingularity
# meta name: Templates
# meta desc: Менеджер быстрых шаблонов с premium emoji и авто-заменой
# meta version: 1.0.1
# meta author: JesterSingularity
# meta url: https://raw.githubusercontent.com/JesterSingularity/SingularityRepo/refs/heads/main/templates.py

from .. import loader, utils
from telethon.tl.types import MessageEntityCustomEmoji
import re, json, os


@loader.tds
class TemplatesMod(loader.Module):
    """Менеджер быстрых шаблонов"""

    strings = {"name": "Templates"}
    FILE = "templates.json"

    # 🔹 ЭТО ГЛАВНОЕ — CONFIG ДЛЯ AYUGRAM
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enabled",
                True,
                "Включить автозамену шаблонов",
                validator=loader.validators.Boolean()
            )
        )

    # ---------- загрузка ----------
    def load_templates(self):
        if not os.path.exists(self.FILE):
            return {}
        with open(self.FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_templates(self):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=4)

    async def client_ready(self, client, db):
        self.templates = self.load_templates()

    # ---------- премиум эмодзи ----------
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

    # =========================================================
    #                     КОМАНДЫ
    # =========================================================

    async def addtplcmd(self, message):
        """ .addtpl .cmd | текст """
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
        """ .deltpl .cmd """
        cmd = utils.get_args_raw(message)

        if cmd not in self.templates:
            return await utils.answer(message, "❌ Шаблон не найден")

        self.templates.pop(cmd)
        self.save_templates()
        await utils.answer(message, f"🗑 Удалён {cmd}")

    async def listtplcmd(self, message):
        """ список шаблонов """
        if not self.templates:
            return await utils.answer(message, "📭 Шаблонов нет")

        text = "📚 Шаблоны:\n\n"
        for k in self.templates:
            text += f"• {k}\n"

        await utils.answer(message, text)

    async def edittplcmd(self, message):
        """ .edittpl .cmd | текст """
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
        """Ответь на сообщение с premium emoji"""
        cmd = utils.get_args_raw(message)

        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, "Ответь на сообщение с emoji")

        ids = []
        if reply.entities:
            for e in reply.entities:
                if isinstance(e, MessageEntityCustomEmoji):
                    ids.append(e.document_id)

        if not ids:
            return await utils.answer(message, "❌ Нет premium emoji")

        if cmd not in self.templates:
            return await utils.answer(message, "❌ Шаблон не найден")

        self.templates[cmd]["emoji_ids"] = ids
        self.save_templates()

        await utils.answer(message, "😎 Emoji сохранены")

    # =========================================================
    #                    АВТОЗАМЕНА
    # =========================================================

    @loader.watcher(outgoing=True)
    async def watcher(self, message):
        if not self.config["enabled"]:
            return

        text = message.raw_text.strip()

        for key, value in self.templates.items():
            if text.startswith(key):
                final_text, entities = self.insert_premium_emojis(
                    value["text"], value.get("emoji_ids", [])
                )
                await message.edit(final_text, formatting_entities=entities)
                return
