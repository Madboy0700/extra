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
        [InlineKeyboardButton(text="Yenile", callback_data="refresh_cat")],
        [InlineKeyboardButton(text="〆 Kapat 〆", callback_data="close")],
    ]
)


@app.on_message(filters.command("cat") & ~BANNED_USERS)
async def cat(c, m: Message):
    r = requests.get("https://api.thecatapi.com/v1/images/search")  # Kedi resmi almak için API'ye istek gönder
    if r.status_code == 200:  # İstek başarılıysa
        data = r.json()  # JSON verisini al
        cat_url = data[0]["url"]  # Kedi resminin URL'sini al
        if cat_url.endswith(".gif"):  # Eğer resim bir GIF ise
            await m.reply_animation(
                cat_url, caption="miyav", reply_markup=close_keyboard
            )
        else:  # Eğer resim bir fotoğraf ise
            await m.reply_photo(cat_url, caption="miyav", reply_markup=close_keyboard)
    else:  # İstek başarısızsa
        await m.reply_text("Kedi resmi alınamadı 🙀")


@app.on_callback_query(filters.regex("refresh_cat") & ~BANNED_USERS)
async def refresh_cat(c, m: CallbackQuery):
    r = requests.get("https://api.thecatapi.com/v1/images/search")  # Kedi resmi almak için API'ye istek gönder
    if r.status_code == 200:  # İstek başarılıysa
        data = r.json()  # JSON verisini al
        cat_url = data[0]["url"]  # Kedi resminin URL'sini al
        if cat_url.endswith(".gif"):  # Eğer resim bir GIF ise
            await m.edit_message_animation(
                cat_url, caption="miyav", reply_markup=close_keyboard
            )
        else:  # Eğer resim bir fotoğraf ise
            await m.edit_message_media(
                InputMediaPhoto(media=cat_url, caption="miyav"),
                reply_markup=close_keyboard,
            )
    else:  # İstek başarısızsa
        await m.edit_message_text("Kedi resmi yenilenemedi 🙀")
