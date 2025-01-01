import datetime
import re

from config import BANNED_USERS
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from YukkiMusic import app
from YukkiMusic.utils.database import (
    deleteall_filters,
    get_filter,
    get_filters_names,
    save_filter,
)
from YukkiMusic.utils.functions import (
    check_format,
    extract_text_and_keyb,
    get_data_and_name,
)
from YukkiMusic.utils.keyboard import ikb

from utils.error import capture_err
from utils.permissions import adminsOnly, member_permissions

from .notes import extract_urls


__MODULE__ = "Filtreler"
__HELP__ = """/filters Tüm filtreleri almak için.
/filter [FILTER_NAME] Bir filtre kaydetmek için (bir mesaja yanıt vererek).

Desteklenen filtre türleri: Metin, Animasyon, Fotoğraf, Belge, Video, video notları, Ses, Sesli mesaj.

Bir filtrede daha fazla kelime kullanmak için:
`/filter Hey_there` "Hey orada" filtresi için.

 /stop [FILTER_NAME] Bir filtreyi durdurmak için.
/stopall Bir sohbetteki tüm filtreleri silmek için (kalıcı olarak).

Metin kaydetmek için markdown veya html de kullanabilirsiniz.

Biçimlendirme ve diğer sözdizimleri hakkında daha fazla bilgi için /markdownhelp komutuna göz atın.
"""


@app.on_message(filters.command("filter") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def save_filters(_, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "**KULLANIM:**\nBir mesaja yanıt vererek /filter [FILTER_NAME] [İÇERİK] ile yeni bir filtre ayarlayın."
            )
        replied_message = message.reply_to_message
        if not replied_message:
            replied_message = message
        data, name = await get_data_and_name(replied_message, message)
        if len(name) < 2:
            return await message.reply_text(
                f"Filtrelemek için {name} 2 kelimeden fazla olmalıdır."
            )
        if data == "error":
            return await message.reply_text(
                "**KULLANIM:**\n__/filter [FILTER_NAME] [İÇERİK]__\n`-----------VEYA-----------`\nBir mesaja yanıt vererek. \n/filter [FILTER_NAME]."
            )
        if replied_message.text:
            _type = "text"
            file_id = None
        if replied_message.sticker:
            _type = "sticker"
            file_id = replied_message.sticker.file_id
        if replied_message.animation:
            _type = "animation"
            file_id = replied_message.animation.file_id
        if replied_message.photo:
            _type = "photo"
            file_id = replied_message.photo.file_id
        if replied_message.document:
            _type = "document"
            file_id = replied_message.document.file_id
        if replied_message.video:
            _type = "video"
            file_id = replied_message.video.file_id
        if replied_message.video_note:
            _type = "video_note"
            file_id = replied_message.video_note.file_id
        if replied_message.audio:
            _type = "audio"
            file_id = replied_message.audio.file_id
        if replied_message.voice:
            _type = "voice"
            file_id = replied_message.voice.file_id
        if replied_message.reply_markup and not re.findall(r"\[.+\,.+\]", data):
            urls = extract_urls(replied_message.reply_markup)
            if urls:
                response = "\n".join(
                    [f"{name}=[{text}, {url}]" for name, text, url in urls]
                )
                data = data + response
        if data:
            data = await check_format(ikb, data)
            if not data:
                return await message.reply_text(
                    "**YANLIŞ BİÇİMLENDİRME, YARDIM bölümünü kontrol edin.**"
                )
        name = name.replace("_", " ")
        _filter = {
            "type": _type,
            "data": data,
            "file_id": file_id,
        }

        chat_id = message.chat.id
        await save_filter(chat_id, name, _filter)
        return await message.reply_text(f"__**Filtre {name} kaydedildi.**__")
    except UnboundLocalError:
        return await message.reply_text(
            "**Yanıt verilen mesaj erişilemez.\n`Mesajı iletin ve tekrar deneyin.`**"
        )


@app.on_message(filters.command("filters") & ~filters.private & ~BANNED_USERS)
@capture_err
async def get_filterss(_, message):
    _filters = await get_filters_names(message.chat.id)  # Sohbetin filtre isimlerini al
    if not _filters:
        return await message.reply_text("**Bu sohbette hiç filtre yok.**")
    _filters.sort()  # Filtreleri sırala
    msg = f"**{message.chat.title}** içindeki filtrelerin listesi:\n"
    for _filter in _filters:
        msg += f"**-** `{_filter}`\n"  # Her bir filtreyi mesajda göster
    await message.reply_text(msg)  # Mesajı gönder


@app.on_message(
    filters.text
    & ~filters.private
    & ~filters.channel
    & ~filters.via_bot
    & ~filters.forwarded
    & ~BANNED_USERS,
    group=1,
)
@capture_err
async def filters_re(_, message):
    from_user = message.from_user if message.from_user else message.sender_chat
    user_id = from_user.id
    chat_id = message.chat.id
    text = message.text.lower().strip()  # Mesajı küçük harfe çevir ve boşlukları temizle
    if not text:
        return
    list_of_filters = await get_filters_names(chat_id)  # Sohbetin filtre isimlerini al
    for word in list_of_filters:
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"  # Filtre kelimesini aramak için düzenli ifade
        if re.search(pattern, text, flags=re.IGNORECASE):  # Filtre kelimesini bul
            _filter = await get_filter(chat_id, word)  # Filtre verilerini al
            data_type = _filter["type"]  # Filtre türünü al
            data = _filter["data"]  # Filtre verisini al
            file_id = _filter.get("file_id")  # Dosya ID'sini al
            keyb = None
            if data:
                # Yer tutucuları gerçek değerlerle değiştir
                if "{app.mention}" in data:
                    data = data.replace("{app.mention}", app.mention)
                if "{GROUPNAME}" in data:
                    data = data.replace("{GROUPNAME}", message.chat.title)
                if "{NAME}" in data:
                    data = data.replace("{NAME}", message.from_user.mention)
                if "{ID}" in data:
                    data = data.replace("{ID}", f"`message.from_user.id`")
                if "{FIRSTNAME}" in data:
                    data = data.replace("{FIRSTNAME}", message.from_user.first_name)
                if "{SURNAME}" in data:
                    sname = message.from_user.last_name or "Yok"
                    data = data.replace("{SURNAME}", sname)
                if "{USERNAME}" in data:
                    susername = message.from_user.username or "Yok"
                    data = data.replace("{USERNAME}", susername)
                if "{DATE}" in data:
                    DATE = datetime.datetime.now().strftime("%Y-%m-%d")
                    data = data.replace("{DATE}", DATE)
                if "{WEEKDAY}" in data:
                    WEEKDAY = datetime.datetime.now().strftime("%A")
                    data = data.replace("{WEEKDAY}", WEEKDAY)
                if "{TIME}" in data:
                    TIME = datetime.datetime.now().strftime("%H:%M:%S")
                    data = data.replace("{TIME}", f"{TIME} UTC")

                if re.findall(r"\[.+\,.+\]", data):  # Eğer klavye varsa
                    keyboard = extract_text_and_keyb(ikb, data)
                    if keyboard:
                        data, keyb = keyboard
            replied_message = message.reply_to_message  # Yanıtlanan mesajı al
            if replied_message:
                replied_user = (
                    replied_message.from_user
                    if replied_message.from_user
                    else replied_message.sender_chat
                )
                if text.startswith("~"):
                    await message.delete()  # Eğer mesaj "~" ile başlıyorsa sil
                if replied_user.id != from_user.id:
                    message = replied_message  # Yanıtlanan mesajı kullan

            # Filtre türüne göre yanıt gönder
            if data_type == "text":
                await message.reply_text(
                    text=data,
                    reply_markup=keyb,
                    disable_web_page_preview=True,
                )
            else:
                if not file_id:
                    continue
            if data_type == "sticker":
                await message.reply_sticker(
                    sticker=file_id,
                )
            if data_type == "animation":
                await message.reply_animation(
                    animation=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "photo":
                await message.reply_photo(
                    photo=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "document":
                await message.reply_document(
                    document=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "video":
                await message.reply_video(
                    video=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "video_note":
                await message.reply_video_note(
                    video_note=file_id,
                )
            if data_type == "audio":
                await message.reply_audio(
                    audio=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "voice":
                await message.reply_voice(
                    voice=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            return  # NOT: Filtre spamını önlemek için


@app.on_message(filters.command("stopall") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def stop_all(_, message):
    _filters = await get_filters_names(message.chat.id)  # Sohbetin filtre isimlerini al
    if not _filters:
        await message.reply_text("**Bu sohbette hiç filtre yok.**")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Evet, sil", callback_data="stop_yes"),
                    InlineKeyboardButton("Hayır, silme", callback_data="stop_no"),
                ]
            ]
        )
        await message.reply_text(
            "**Tüm filtreleri kalıcı olarak silmek istediğinizden emin misiniz?**",
            reply_markup=keyboard,
        )


@app.on_callback_query(filters.regex("stop_(.*)") & ~BANNED_USERS)
async def stop_all_cb(_, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)  # Kullanıcının izinlerini al
    permission = "can_change_info"
    if permission not in permissions:
        return await cb.answer(
            f"Bu izne sahip değilsiniz.\nİzin: {permission}",
            show_alert=True,
        )
    input = cb.data.split("_", 1)[1]  # Callback verisini al
    if input == "yes":
        stoped_all = await deleteall_filters(chat_id)  # Tüm filtreleri sil
        if stoped_all:
            return await cb.message.edit(
                "**Tüm filtreler başarıyla silindi.**"
            )
    if input == "no":
        await cb.message.reply_to_message.delete()  # Yanıtlanan mesajı sil
        await cb.message.delete()  # Callback mesajını sil # Yukarıdaki kodun devamı yok, ancak burada genel bir özet ve açıklama yapabilirim.

# Bu kod, Telegram botu için filtre yönetimi işlevselliği sağlar.
# Kullanıcılar belirli komutlar ile filtreleri kaydedebilir, görüntüleyebilir ve silebilirler.

# Filtreler, belirli kelimeleri veya ifadeleri tanımlamak için kullanılır ve bu kelimelerle eşleşen mesajlara yanıt olarak belirli içerikler gönderilir.
# Örneğin, bir kullanıcı "/filter merhaba" komutunu kullanarak "merhaba" kelimesini filtreleyebilir ve bu kelime kullanıldığında bot belirli bir yanıt verebilir.

# Ayrıca, kullanıcılar "/stopall" komutunu kullanarak tüm filtreleri kalıcı olarak silebilirler. Bu işlem için onay alınır.

# Kodda kullanılan bazı önemli fonksiyonlar:
# - save_filters: Yeni bir filtre kaydeder.
# - get_filterss: Mevcut filtrelerin listesini alır.
# - filters_re: Kullanıcı mesajlarını kontrol eder ve filtreleri uygular.
# - stop_all: Tüm filtreleri silmek için onay alır.
# - stop_all_cb: Kullanıcının onayına göre tüm filtreleri siler veya işlemi iptal eder.

# Eğer daha fazla bilgi veya belirli bir bölüm hakkında daha fazla açıklama isterseniz, lütfen belirtin!
