import requests
from config import BANNED_USERS
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)
from YukkiMusic import app


# Klavye düzeni
close_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="Yenile", callback_data="refresh_dog")],
        [InlineKeyboardButton(text="〆 Kapat 〆", callback_data="close")],
    ]
)


@app.on_message(filters.command(["dogs", "dog"]) & ~BANNED_USERS)
async def dog(c, m: Message):
    r = requests.get("https://random.dog/woof.json")  # Rastgele köpek resmi almak için API'ye istek gönder
    if r.status_code == 200:  # İstek başarılıysa
        data = r.json()  # JSON verisini al
        dog_url = data["url"]  # Köpek resminin URL'sini al
        if dog_url.endswith(".gif"):  # Eğer resim bir GIF ise
            await m.reply_animation(dog_url, reply_markup=close_keyboard)  # GIF'i gönder
        else:
            await m.reply_photo(dog_url, reply_markup=close_keyboard)  # Fotoğrafı gönder
    else:
        await m.reply_text("Köpek resmi alınamadı 🐕")  # İstek başarısızsa mesaj gönder


@app.on_callback_query(filters.regex("refresh_dog") & ~BANNED_USERS)
async def refresh_dog(c, m: CallbackQuery):
    r = requests.get("https://random.dog/woof.json")  # Yeniden köpek resmi almak için API'ye istek gönder
    if r.status_code == 200:  # İstek başarılıysa
        data = r.json()  # JSON verisini al
        dog_url = data["url"]  # Köpek resminin URL'sini al
        if dog_url.endswith(".gif"):  # Eğer resim bir GIF ise
            await m.edit_message_animation(dog_url, reply_markup=close_keyboard)  # GIF'i güncelle
        else:
            await m.edit_message_media(
                InputMediaPhoto(media=dog_url),  # Fotoğrafı güncelle
                reply_markup=close_keyboard,
            )
    else:
        await m.edit_message_text("Köpek resmi yenilenemedi 🐕")  # İstek başarısızsa mesaj gönder
