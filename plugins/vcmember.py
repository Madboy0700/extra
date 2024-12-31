from pyrogram import filters
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
        # Sohbetin dilini al
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except BaseException:
        # Eğer dil bilgisi alınamazsa varsayılan olarak İngilizceyi kullan
        _ = get_string("en")

    # Başlangıç mesajı
    msg = await message.reply_text(_["V_C_1"])

    # Yardımcı botu al
    userbot = await get_assistant(message.chat.id)
    
    TEXT = ""
    
    try:
        # Yardımcı botun katıldığı üyeleri döngü ile al
        async for m in userbot.get_call_members(message.chat.id):
            chat_id = m.chat.id
            username = m.chat.username
            is_hand_raised = m.is_hand_raised
            is_video_enabled = m.is_video_enabled
            is_left = m.is_left
            is_screen_sharing_enabled = m.is_screen_sharing_enabled
            is_muted = bool(m.is_muted and not m.can_self_unmute)
            is_speaking = not m.is_muted

            # Kullanıcının özel bir sohbeti var mı?
            if m.chat.type != ChatType.PRIVATE:
                title = m.chat.title
            else:
                try:
                    title = (await client.get_users(chat_id)).mention
                except BaseException:
                    title = m.chat.first_name

            # Kullanıcı bilgilerini metne formatla
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
        
        # Mesajın uzunluğu 4000 karakteri geçiyorsa, linke dönüştür
        if len(TEXT) < 4000:
            await msg.edit(TEXT or _["V_C_3"])
        else:
            # Yukkibin servisi ile uzun metni bir linke dönüştür
            link = await Yukkibin(TEXT)
            await msg.edit(
                _["V_C_4"].format(link),
                disable_web_page_preview=True,
            )
    except ValueError as e:
        # Hata oluşursa, kullanıcıya hata mesajı göster
        await msg.edit(_["V_C_5"])
