from .. import loader, utils
from telethon.tl.types import MessageEntityCustomEmoji
import re, json, os


@loader.tds
class TemplatesMod(loader.Module):
    """Менеджер шаблонов"""

    strings = {"name": "Templates"}

    FILE = "templates.json"
    STATE_FILE = "templates_state.json"

    # ---------------- LOAD ----------------
    async def client_ready(self, client, db):
        self.templates = self.load_templates()

    def load_templates(self):
        if not os.path.exists(self.FILE):
            return {}
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_templates(self):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=4)

    # ---------------- STATE ----------------
    def is_enabled(self):
        try:
            with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                return f.read().strip() == "true"
        except:
            return True  # по умолчанию включено

    # ---------------- EMOJI ----------------
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

    # ---------------- WATCHER ----------------
    @loader.watcher(outgoing=True)
    async def watcher(self, message):
        if not self.is_enabled():
            return

        text = message.raw_text.strip()

        for key, value in self.templates.items():
            if text.startswith(key):
                final_text, entities = self.insert_premium_emojis(
                    value.get("text", ""),
                    value.get("emoji_ids", [])
                )

                await message.edit(final_text, formatting_entities=entities)
                return
