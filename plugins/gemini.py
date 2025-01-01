import requests
from MukeshAPI import api
from pyrogram import filters
from pyrogram.enums import ChatAction
from YukkiMusic import app


@app.on_message(filters.command(["gemini"]))
async def gemini_handler(client, message):
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)  # Kullanıcıya yazma eylemi göster
    if (
        message.text.startswith(f"/gemini@{app.username}")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]  # Kullanıcının girdiği metni al
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text  # Yanıtlanan mesajın metnini al
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])  # Komutun geri kalanını al
        else:
            await message.reply_text("Örnek :- `/gemini kimdir lord ram`")  # Kullanıcıya örnek ver
            return

    try:
        response = api.gemini(user_input)  # API'den yanıt al
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)  # Yazma eylemi göster
        x = response["results"]  # API yanıtındaki sonuçları al
        if x:
            await message.reply_text(x, quote=True)  # Sonuçları yanıt olarak gönder
        else:
            await message.reply_text("Üzgünüm! Lütfen tekrar deneyin.")  # Sonuç yoksa hata mesajı gönder
    except requests.exceptions.RequestException as e:
        pass  # Hata durumunda hiçbir şey yapma
