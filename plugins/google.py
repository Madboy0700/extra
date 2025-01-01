from googlesearch import search
from pyrogram import filters
from YukkiMusic import app


@app.on_message(filters.command(["google", "gle"]))
async def google(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Örnek:\n\n`/google lord ram`")
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text  # Yanıtlanan mesajın metnini al
    else:
        user_input = " ".join(message.command[1:])  # Komutun geri kalanını al
    b = await message.reply_text("**Google'da arama yapılıyor...**")
    try:
        a = search(user_input, advanced=True)  # Google'da arama yap
        txt = f"Arama Sorgusu: {user_input}\n\nSonuçlar"
        for result in a:
            txt += f"\n\n[❍ {result.title}]({result.url})\n<b>{result.description}</b>"  # Sonuçları formatla
        await b.edit(
            txt,
            disable_web_page_preview=True,  # Web sayfası önizlemesini devre dışı bırak
        )
    except Exception as e:
        await b.edit(str(e))  # Hata durumunda hata mesajını göster


__MODULE__ = "Google"
__HELP__ = """/google [sorgu] - Google'da arama yap ve sonuçları getir"""
