from config import BANNED_USERS
from pyrogram import filters
from pyrogram.enums import ChatAction
from TheApi import api
from YukkiMusic import app


@app.on_message(filters.command(["chatgpt", "ai", "ask"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Örnek:\n\n`/ai basit bir web sitesi kodu yaz html css, js kullanarak?`"
        )
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text  # Yanıtlanan mesajın metnini al
    else:
        user_input = " ".join(message.command[1:])  # Komutun geri kalanını birleştir

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)  # Yazma eylemi gönder
    results = await api.chatgpt(user_input)  # API'den yanıt al
    await message.reply_text(results)  # Yanıtı gönder


__MODULE__ = "CʜᴀᴛGᴘᴛ"  # Modül adı
__HELP__ = """
/advice - Bot tarafından rastgele tavsiye al
/ai [soru] - ChatGPT'nin AI'si ile sorunu sor
/gemini [soru] - Google'ın Gemini AI'si ile sorunu sor
"""
