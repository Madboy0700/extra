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
    # Dil ayarlarını almak
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)  # Dil metinlerini al
    except BaseException:
        _ = get_string("en")  # Hata durumunda varsayılan olarak İngilizce kullan

    # Başlangıçta mesaj gönder
    msg = await message.reply_text(_["V_C_1"])
    
    # Chat için userbot'ı al
    userbot = await get_assistant(message.chat.id)
    
    # Katılımcı bilgilerini tutacak değişken
    TEXT = ""
    
    try:
        # Görüşme üyelerini al
        async for m in userbot.get_call_members(message.chat.id):
            chat_id = m.chat.id
            username = m.chat.username
            is_hand_raised = m.is_hand_raised
            is_video_enabled = m.is_video_enabled
            is_left = m.is_left
            is_screen_sharing_enabled = m.is_screen_sharing_enabled
            is_muted = bool(m.is_muted and not m.can_self_unmute)
            is_speaking = not m.is_muted

            # Katılımcı adı ve bilgileri için formatlama
            if m.chat.type != ChatType.PRIVATE:
                title = m.chat.title  # Grup adı
            else:
                try:
                    title = (await client.get_users(chat_id)).mention  # Kullanıcı adı
                except BaseException:
                    title = m.chat.first_name  # Kullanıcının ismi

            # Katılımcı bilgilerini metne ekle
            TEXT += _["V_C_2"].format(
                title,
                chat_id,
                username or "N/A",  # Kullanıcı adı yoksa 'N/A' yazdır
                is_video_enabled,
                is_screen_sharing_enabled,
                is_hand_raised,
                is_muted,
                is_speaking,
                is_left,
            )
            TEXT += "\n\n"
        
        # Mesaj uzunluğu 4000 karakteri geçiyorsa, Yukkibin ile link oluştur
        if len(TEXT) < 4000:
            await msg.edit(TEXT or _["V_C_3"])  # Eğer metin boşsa, alternatif mesaj
        else:
            link = await Yukkibin(TEXT)  # Uzun metin için Yukkibin linki oluştur
            await msg.edit(
                _["V_C_4"].format(link),  # Linki mesajda göster
                disable_web_page_preview=True,
            )
    
    except ValueError as e:
        # Bir hata oluşursa, hata mesajı gönder
        await msg.edit(_["V_C_5"])
