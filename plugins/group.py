from pyrogram import enums, filters
from YukkiMusic import app

from utils.permissions import adminsOnly


@app.on_message(filters.command("removephoto"))
@adminsOnly("can_change_info")
async def deletechatphoto(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("**İşleniyor....**")
    admin_check = await app.get_chat_member(chat_id, user_id)
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**Bu komut gruplarda çalışır!**")
    try:
        if admin_check.privileges.can_change_info:
            await app.delete_chat_photo(chat_id)
            await msg.edit(
                "**Grup profil fotoğrafı kaldırıldı!\nTarafından:** {}".format(
                    message.from_user.mention
                )
            )
    except BaseException:
        await msg.edit(
            "**Kullanıcının grup fotoğrafını kaldırmak için bilgi değiştirme yetkisine sahip olması gerekir!**"
        )


@app.on_message(filters.command("setphoto"))
@adminsOnly("can_change_info")
async def setchatphoto(_, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("İşleniyor...")
    admin_check = await app.get_chat_member(chat_id, user_id)
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("`Bu komut gruplarda çalışır!`")
    elif not reply:
        await msg.edit("**Bir fotoğraf veya belgeye yanıt verin.**")
    elif reply:
        try:
            if admin_check.privileges.can_change_info:
                photo = await reply.download()
                await message.chat.set_photo(photo=photo)
                await msg.edit_text(
                    "**Yeni grup profil fotoğrafı değiştirildi!\nTarafından:** {}".format(
                        message.from_user.mention
                    )
                )
            else:
                await msg.edit("**Bir şeyler yanlış gitti, başka bir fotoğraf deneyin!**")

        except BaseException:
            await msg.edit(
                "**Kullanıcının grup fotoğrafını değiştirmek için bilgi değiştirme yetkisine sahip olması gerekir!**"
            )


@app.on_message(filters.command("settitle"))
@adminsOnly("can_change_info")
async def setgrouptitle(_, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("İşleniyor...")
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**Bu komut gruplarda çalışır!**")
    elif reply:
        try:
            title = message.reply_to_message.text
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_title(title)
                await msg.edit(
                    "**Yeni grup adı değiştirildi!\nTarafından:** {}".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**Kullanıcının grup adını değiştirmek için bilgi değiştirme yetkisine sahip olması gerekir!**"
            )
    elif len(message.command) > 1:
        try:
            title = message.text.split(None, 1)[1]
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_title(title)
                await msg.edit(
                    "**Yeni grup adı değiştirildi!\nTarafından:** {}".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**Kullanıcının grup adını değiştirmek için bilgi değiştirme yetkisine sahip olması gerekir!**"
            )

    else:
        await msg.edit(
            "**Bir metne yanıt vermeniz veya grup adını değiştirmek için bir metin vermeniz gerekiyor!**"
        )


@app.on_message(filters.command(["setdiscription", "setdesc"]))
@adminsOnly("can_change_info")
async def setg_discription(_, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("**İşleniyor...**")
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**Bu komut gruplarda çalışır!**")
    elif reply:
        try:
            discription = message.reply_to_message.text
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_description(discription)
                await msg.edit(
                    "**Grup açıklaması değiştirildi!**\nTarafından {}".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**Kullanıcının grup açıklamasını değiştirmek için bilgi değiştirme yetkisine sahip olması gerekir!**"
            )
    elif len(message.command) > 1:
        try:
            discription = message.text.split(None, 1)[1]
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_description(discription)
                await msg.edit(
                    "**Grup açıklaması değiştirildi!**\nTarafından {}".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**Kullanıcının grup açıklamasını değiştirmek için bilgi değiştirme yetkisine sahip olması gerekir!**"
            )
    else:
        await msg.edit(
            "**Bir metne yanıt vermeniz veya grup açıklamasını değiştirmek için bir metin vermeniz gerekiyor!**"
        )
