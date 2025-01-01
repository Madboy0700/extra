import io
import os
import os.path
import time
from inspect import getfullargspec
from os.path import exists, isdir

from pyrogram import filters
from pyrogram.types import Message
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS

from utils.error import capture_err

MAX_MESSAGE_SIZE_LIMIT = 4095  # Maksimum mesaj boyutu sınırı


@app.on_message(filters.command("ls") & ~filters.forwarded & ~filters.via_bot & SUDOERS)
@capture_err
async def lst(_, message):
    prefix = message.text.split()[0][0]  # Komutun ön ekini al
    chat_id = message.chat.id  # Sohbet ID'sini al
    path = os.getcwd()  # Geçerli çalışma dizinini al
    text = message.text.split(" ", 1)  # Mesajı boşlukla ayır
    directory = None
    if len(text) > 1:
        directory = text[1].strip()  # Dizin adını al
        path = directory
    if not exists(path):  # Eğer dizin veya dosya yoksa
        await eor(
            message,
            text=f"Böyle bir dizin veya dosya yok `{directory}` adında, lütfen kontrol edin!",
        )
        return
    if isdir(path):  # Eğer verilen yol bir dizin ise
        if directory:
            msg = "Dizin ve Dosyalar `{}` içinde:\n\n".format(path)
            lists = os.listdir(path)  # Dizin içeriğini al
        else:
            msg = "Geçerli Dizin içindeki Dizin ve Dosyalar:\n\n"
            lists = os.listdir(path)
        files = ""
        folders = ""
        for contents in sorted(lists):  # İçeriği sıralı olarak döngüye al
            thepathoflight = path + "/" + contents
            if not isdir(thepathoflight):  # Eğer içerik bir dizin değilse
                size = os.stat(thepathoflight).st_size  # Dosya boyutunu al
                if contents.endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += "🎵 " + f"`{contents}`\n"  # Müzik dosyası
                if contents.endswith((".opus")):
                    files += "🎙 " + f"`{contents}`\n"  # Ses dosyası
                elif contents.endswith(
                    (".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")
                ):
                    files += "🎞 " + f"`{contents}`\n"  # Video dosyası
                elif contents.endswith(
                    (".zip", ".tar", ".tar.gz", ".rar", ".7z", ".xz")
                ):
                    files += "🗜 " + f"`{contents}`\n"  # Arşiv dosyası
                elif contents.endswith(
                    (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")
                ):
                    files += "🖼 " + f"`{contents}`\n"  # Resim dosyası
                elif contents.endswith((".exe", ".deb")):
                    files += "⚙️ " + f"`{contents}`\n"  # Uygulama dosyası
                elif contents.endswith((".iso", ".img")):
                    files += "💿 " + f"`{contents}`\n"  # Disk imajı
                elif contents.endswith((".apk", ".xapk")):
                    files += "📱 " + f"`{contents}`\n"  # Android uygulama dosyası
                elif contents.endswith((".py")):
                    files += "🐍 " + f"`{contents}`\n"  # Python dosyası
                else:
                    files += "📄 " + f"`{contents}`\n"  # Diğer dosyalar
            else:
                folders += f"📁 `{contents}`\n"  # Dizinleri listele
        if files or folders:
            msg = msg + folders + files  # Mesajı güncelle
        else:
            msg = msg + "__boş yol__"  # Eğer içerik yoksa
    else:  # Eğer verilen yol bir dosya ise
        size = os.stat(path).st_size  # Dosya boyutunu al
        msg = "Verilen dosyanın detayları:\n\n"
        if path.endswith((".mp3", ".flac", ".wav", ".m4a")):
            mode = "🎵 "  # Müzik dosyası simgesi
        elif path.endswith((".opus")):
            mode = "🎙 "  # Ses dosyası simgesi
        elif path.endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
            mode = "🎞 "  # Video dosyası simgesi
        elif path.endswith((".zip", ".tar", ".tar.gz", ".rar", ".7z", ".xz")):
            mode = "🗜 "  # Arşiv dosyası simgesi
        elif path.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")):
            mode = "🖼 "  # Resim dosyası simgesi
        elif path.endswith((".exe", ".deb")):
            mode = "⚙️ "  # Uygulama dosyası simgesi
        elif path.endswith((".iso", ".img")):
            mode = "💿 "  # Disk imajı simgesi
        elif path.endswith((".apk", ".xapk")):
            mode = "📱 "  # Android uygulama dosyası simgesi
        elif path.endswith((".py")):
            mode = "🐍 "  # Python dosyası simgesi
        else:
            mode = "📄 "  # Diğer dosyalar için simge

        time2 = time.ctime(os.path.getmtime(path))  # Son değiştirilme zamanı
        time3 = time.ctime(os.path.getatime(path))  # Son erişim zamanı
        msg += f"**Konum :** `{path}`\n"
        msg += f"**Sembol :** `{mode}`\n"
        msg += f"**Boyut :** `{humanbytes(size)}`\n"  # Boyutu insan okunur formatta göster
        msg += f"**Son Değiştirilme Zamanı:** `{time2}`\n"
        msg += f"**Son Erişim Zamanı:** `{time3}`"

    if len(msg) > MAX_MESSAGE_SIZE_LIMIT:  # Mesaj boyutu sınırını kontrol et
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "ls.txt"  # Dosya adını ayarla
            await app.send_document(
                chat_id,
                out_file,
                caption=path,  # Dosya içeriğini gönder
            )
            await message.delete()  # Orijinal mesajı sil
    else:
        await eor(message, text=msg)  # Mesajı yanıtla


@app.on_message(filters.command("rm") & ~filters.forwarded & ~filters.via_bot & SUDOERS)
@capture_err
async def rm_file(client, message):
    if len(message.command) < 2:  # Eğer dosya adı verilmemişse
        return await eor(message, text="Lütfen silinecek bir dosya adı verin.")
    file = message.text.split(" ", 1)[1]  # Dosya adını al
    if exists(file):  # Eğer dosya mevcutsa
        os.remove(file)  # Dosyayı sil
        await eor(message, text=f"{file} silindi.")
    else:
        await eor(message, text=f"{file} mevcut değil!")


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args  # Fonksiyonun argümanlarını al
    return await func(**{k: v for k, v in kwargs.items() if k in spec})  # Fonksiyonu çağır
