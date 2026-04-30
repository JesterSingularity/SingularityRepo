# ==AyugramPlugin==
# @name         Templates Control
# @version      1.0.0
# @description  Управление Hikka Templates
# @author       JesterSingularity
# @command      tplon, tploft
# ==/AyugramPlugin==

import os
from base_plugin import BasePlugin, HookResult, HookStrategy
from client_utils import send_message


__id__ = "templates_control"
__name__ = "Templates Control"
__version__ = "1.0.0"


class TemplatesControl(BasePlugin):

    STATE_FILE = "templates_state.json"

    def set_state(self, value: bool):
        with open(self.STATE_FILE, "w", encoding="utf-8") as f:
            f.write("true" if value else "false")

    def tplon(self, message, args):
        self.set_state(True)
        send_message({
            "peer": message.peer,
            "message": "✅ Templates включены"
        })

    def tploft(self, message, args):
        self.set_state(False)
        send_message({
            "peer": message.peer,
            "message": "⛔ Templates выключены"
        })
