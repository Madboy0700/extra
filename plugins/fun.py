import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from YukkiMusic import app


@app.on_message(
    filters.command(
        [
            "dice",
            "ludo",
            "dart",
            "basket",
            "basketball",
            "football",
            "slot",
            "bowling",
            "jackpot",
        ]
    )
)
async def dice(c, m: Message):
    command = m.text.split()[0]
    if command == "/dice" or command == "/ludo":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔄", callback_data="send_dice")]]
        )
        value = await c.send_dice(m.chat.id, reply_markup=keyboard)

    elif command == "/dart":
        value = await c.send_dice(m.chat.id, emoji="🎯", reply_to_message_id=m.id)
        await value.reply_text("Skorunuz: {0}".format(value.dice.value))

    elif command == "/basket" or command == "/basketball":
        basket = await c.send_dice(m.chat.id, emoji="🏀", reply_to_message_id=m.id)
        await basket.reply_text("Skorunuz: {0}".format(basket.dice.value))

    elif command == "/football":
        value = await c.send_dice(m.chat.id, emoji="⚽", reply_to_message_id=m.id)
        await value.reply_text("Skorunuz: {0}".format(value.dice.value))

    elif command == "/slot" or command == "/jackpot":
        value = await c.send_dice(m.chat.id, emoji="🎰", reply_to_message_id=m.id)
        await value.reply_text("Skorunuz: {0}".format(value.dice.value))
        
    elif command == "/bowling":
        value = await c.send_dice(m.chat.id, emoji="🎳", reply_to_message_id=m.id)
        await value.reply_text("Skorunuz: {0}".format(value.dice.value))


bored_api_url = "https://apis.scrimba.com/bored/api/activity"


@app.on_message(filters.command("bored", prefixes="/"))
async def bored_command(client, message):
    response = requests.get(bored_api_url)
    if response.status_code == 200:
        data = response.json()
        activity = data.get("activity")
        if activity:
            await message.reply(f"Canınız sıkılıyor mu? Nasıl olur:\n\n {activity}")
        else:
            await message.reply("Hiçbir aktivite bulunamadı.")
    else:
        await message.reply("Aktivite almakta başarısız olundu.")


@app.on_callback_query(filters.regex(r"send_dice"))
async def dice_again(client, query):
    try:
        await app.edit_message_text(
            query.message.chat.id, query.message.id, query.message.dice.emoji
        )
    except BaseException:
        pass
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄", callback_data="send_dice")]]
    )
    await client.send_dice(query.message.chat.id, reply_markup=keyboard)


__MODULE__ = "Eğlence"
__HELP__ = """
**Eğlenmek için:**

• `/dice`: Bir zar atar.
• `/ludo`: Ludo oynar.
• `/dart`: Dart atar.
• `/basket` veya `/basketball`: Basketbol oynar.
• `/football`: Futbol oynar.
• `/slot` veya `/jackpot`: Jackpot oynar.
• `/bowling`: Bowling oynar.
• `/bored`: Canınız sıkılıyorsa rastgele bir aktivite alır.
"""
