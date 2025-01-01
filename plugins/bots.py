import asyncio

from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from YukkiMusic import app


@app.on_message(filters.command("bots") & filters.group)
async def bots(client, message):
    try:
        botList = []  # Botların listesini tutmak için boş bir liste oluştur
        async for bot in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BOTS
        ):
            botList.append(bot.user)  # Botları listeye ekle
        lenBotList = len(botList)  # Bot sayısını al
        text3 = f"**Bot Listesi - {message.chat.title}**\n\n🤖 Botlar\n"
        while len(botList) > 1:  # Liste 1'den fazla bot içeriyorsa
            bot = botList.pop(0)  # İlk botu çıkar
            text3 += f"├ @{bot.username}\n"  # Botun kullanıcı adını ekle
        else:  # Liste 1 bot içeriyorsa
            bot = botList.pop(0)  # Son botu çıkar
            text3 += f"└ @{bot.username}\n\n"  # Botun kullanıcı adını ekle
            text3 += f"**Toplam Bot Sayısı**: {lenBotList}**"  # Toplam bot sayısını ekle
            await app.send_message(message.chat.id, text3)  # Mesajı gönder
    except FloodWait as e:  # FloodWait hatası alırsak
        await asyncio.sleep(e.value)  # Belirtilen süre kadar bekle


__MODULE__ = "Botlar"  # Modül adı
__HELP__ = """
**Botlar**

• /bots - Grubun içindeki botların listesini al.
"""
