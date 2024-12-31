from pyrogram import Client, filters
from pyrogram.enums import ChatType
from strings import get_string
from YukkiMusic import app
from YukkiMusic.utils import Yukkibin
from YukkiMusic.utils.database import get_assistant, get_lang


@app.on_message(
    filters.command(["vcuser", "vcusers", "vcmember", "vcmembers"]) & filters.admin
)
async def vc_members(client, message):
    try:
        # Dil ayarlarını al
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except Exception:
        # Dil ayarı alınamazsa varsayılan dil olarak İngilizceyi kullan
        _ = get_string("en")

    # Başlangıçta bir cevap mesajı gönder
    msg = await message.reply_text(_["V_C_1"])

    # Yardımcı botu al
    userbot = await get_assistant(message.chat.id)

    TEXT = ""
    try:
        # Sesli sohbetin üyelerini gez
        async for m in userbot.get_call_members(message.chat.id):
            chat_id = m.chat.id
            username = m.chat.username
            is_hand_raised = m.is_hand_raised
            is_video_enabled = m.is_video_enabled
            is_left = m.is_left
            is_screen_sharing_enabled = m.is_screen_sharing_enabled
            is_muted = bool(m.is_muted and not m.can_self_unmute)
            is_speaking = not m.is_muted

            # Eğer kullanıcı bir grup içindeyse, grup başlığını al
            if m.chat.type != ChatType.PRIVATE:
                title = m.chat.title
            else:
                try:
                    # Eğer kullanıcı özel mesajda ise, kullanıcıyı al
                    title = (await client.get_users(chat_id)).mention
                except Exception:
                    # Kullanıcı adı alınamazsa, adını al
                    title = m.chat.first_name

            # Üye bilgilerini formata yerleştir
            TEXT += _["V_C_2"].format(
                title,
                chat_id,
                username,
                is_video_enabled,
                is_screen_sharing_enabled,
                is_hand_raised,
                is_muted,
                is_speaking,
                is_left,
            )
            TEXT += "\n\n"

        # Eğer metin çok uzunsa, Yukkibin ile kısalt ve linki gönder
        if len(TEXT) < 4000:
            await msg.edit(TEXT or _["V_C_3"])
        else:
            link = await Yukkibin(TEXT)
            await msg.edit(
                _["V_C_4"].format(link),
                disable_web_page_preview=True,
            )

    except ValueError as e:
        # Eğer bir hata oluşursa, hata mesajı gönder
        await msg.edit(_["V_C_5"])
