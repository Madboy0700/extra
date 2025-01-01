#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors.exceptions.bad_request_400 import UserAlreadyParticipant
from pyrogram.types import ChatJoinRequest
from YukkiMusic import app
from YukkiMusic.core.mongo import mongodb
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.keyboard import ikb

from utils.permissions import adminsOnly, member_permissions


approvaldb = mongodb.autoapprove


def smallcap(text):
    trans_table = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢABCDEFGHIJKLMNOPQRSTUVWXYZ0𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    )
    return text.translate(trans_table)


@app.on_message(filters.command("autoapprove") & filters.group)
@adminsOnly("can_change_info")
async def approval_command(client, message):
    chat_id = message.chat.id
    chat = await approvaldb.find_one({"chat_id": chat_id})
    if chat:
        mode = chat.get("mode", "")
        if not mode:
            mode = "manual"
            await approvaldb.update_one(
                {"chat_id": chat_id},
                {"$set": {"mode": mode}},
                upsert=True,
            )
        if mode == "automatic":
            switch = "manual"
            mdbutton = "ᴀᴜᴛᴏᴍᴀᴛɪᴄ"
        else:
            switch = "automatic"
            mdbutton = "ᴍᴀɴɴᴜᴀʟ"
        buttons = {
            "Tᴜʀɴ ᴏғғ": "approval_off",
            f"{mdbutton}": f"approval_{switch}",
        }
        keyboard = ikb(buttons, 1)
        await message.reply(
            "**Otomatik Onay Bu sohbet için: Etkin.**", reply_markup=keyboard
        )
    else:
        buttons = {"Tᴜʀɴ ᴏɴ ": "approval_on"}
        keyboard = ikb(buttons, 1)
        await message.reply(
            "**Otomatik Onay Bu sohbet için: Devre Dışı.**", reply_markup=keyboard
        )


@app.on_callback_query(filters.regex("approval(.*)"))
async def approval_cb(client, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDOERS:
            return await cb.answer(
                f"Gerekli izne sahip değilsiniz.\n İzin: {permission}",
                show_alert=True,
            )
    command_parts = cb.data.split("_", 1)
    option = command_parts[1]
    if option == "off":
        if await approvaldb.count_documents({"chat_id": chat_id}) > 0:
            approvaldb.delete_one({"chat_id": chat_id})
            buttons = {"ᴛᴜʀɴ ᴏɴ": "approval_on"}
            keyboard = ikb(buttons, 1)
            return await cb.edit_message_text(
                "**Aᴜᴛᴏᴀᴘᴘʀᴏᴠᴀʟ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ: Dɪsᴀʙʟᴇᴅ.**",
                reply_markup=keyboard,
            )
    if option == "on":
        switch = "manual"
        mode = "automatic"
    if option == "automatic":
        switch = "manual"
        mode = option
    if option == "manual":
        switch = "automatic"
        mode = option
    await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True,
    )
    chat = await approvaldb.find_one({"chat_id": chat_id})
    mode = smallcap(chat["mode"])
    buttons = {"ᴛᴜʀɴ ᴏғғ": "approval_off", f"{mode}": f"approval_{switch}"}
    keyboard = ikb(buttons, 1)
    await cb.edit_message_text(
        "**Otomatik Onay Bu sohbet için: Etkin.**", reply_markup=keyboard
    )


@app.on_message(filters.command("approveall") & filters.group)
@adminsOnly("can_restrict_members")
async def clear_pending_command(client, message):
    a = await message.reply_text("ᴡᴀɪᴛ.....")
    chat_id = message.chat.id
    await app.approve_all_chat_join_requests(chat_id)
    await a.edit("Eğer herhangi bir kullanıcı onay bekliyorsa, ben onu onaylıyorum.")
    await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"pending_users": []}},
    )


@app.on_message(filters.command("clearpending") & filters.group)
@adminsOnly("can_restrict_members")
async def clear_pending_command(client, message):
    chat_id = message.chat.id
    result = await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"pending_users": []}},
    )
    if result.modified_count > 0:
        await message.reply_text("Bekleyen kullanıcılar temizlendi.")
    else:
        await message.reply_text("Temizlenecek bekleyen kullanıcı yok.")


@app.on_chat_join_request(filters.group)
async def accept(client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    chat_id = await approvaldb.find_one({"chat_id": chat.id})
    if chat_id:
        mode = chat_id["mode"]
        if mode == "automatic":
            await app.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
            return
        if mode == "manual":
            is_user_in_pending = await approvaldb.count_documents(
                {"chat_id": chat.id, "pending_users": int(user.id)}
            )
            if is_user_in_pending == 0:
                await approvaldb.update_one(
                    {"chat_id": chat.id},
                    {"$addToSet": {"pending_users": int(user.id)}},
                    upsert=True,
                )
                buttons = {
                    "ᴀᴄᴄᴇᴘᴛ": f"manual_approve_{user.id}",
                    "ᴅᴇᴄʟɪɴᴇ": f"manual_decline_{user.id}",
                }
                keyboard = ikb(buttons, int(2))
                text = f"**Kullanıcı: {user.mention} grubumuza katılmak için bir istek gönderdi. Herhangi bir yönetici bunu kabul edebilir veya reddedebilir.**"
                admin_data = [
                    i
                    async for i in app.get_chat_members(
                        chat_id=message.chat.id,
                        filter=ChatMembersFilter.ADMINISTRATORS,
                    )
                ]
                for admin in admin_data:
                    if admin.user.is_bot or admin.user.is_deleted:
                        continue
                    text += f"[\u2063](tg://user?id={admin.user.id})"
                return await app.send_message(chat.id, text, reply_markup=keyboard)


@app.on_callback_query(filters.regex("manual_(.*)"))
async def manual(app, cb):
    chat = cb.message.chat
    from_user = cb.from_user
    permissions = await member_permissions(chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDOERS:
            return await cb.answer(
                f"Gerekli izne sahip değilsiniz.\n İzin: {permission}",
                show_alert=True,
            )
    datas = cb.data.split("_", 2)
    dis = datas[1]
    id = datas[2]
    if dis == "approve":
        try:
            await app.approve_chat_join_request(chat_id=chat.id, user_id=id)
        except UserAlreadyParticipant:
            await cb.answer(
                "Kullanıcı, grubunuzda herhangi biri tarafından onaylandı.",
                show_alert=True,
            )
            return await cb.message.delete()

    if dis == "decline":
        try:
            await app.decline_chat_join_request(chat_id=chat.id, user_id=id)
        except Exception as e:
            if "messages.HideChatJoinRequest" in str(e):
                await cb.answer(
                    "Kullanıcı, grubunuzda herhangi biri tarafından onaylandı.",
                    show_alert=True,
                )

    await approvaldb.update_one(
        {"chat_id": chat.id},
        {"$pull": {"pending_users": int(id)}},
    )
    return await cb.message.delete()


__MODULE__ = "Aᴘᴘʀᴏᴠᴇ"
__HELP__ = """
command: /autoapprove

Bu modül, bir kullanıcı tarafından grubunuzun davet bağlantısı aracılığıyla gönderilen sohbet katılma isteklerini otomatik olarak kabul etmeye yardımcı olur.

Modlar: /autoapprove komutunu grubunuzda gönderdiğinizde, otomatik onay etkin değilse "butonu aç" mesajını göreceksiniz. Eğer zaten etkinse, aşağıda belirtilen iki moddan birini göreceksiniz ve kullanımı hakkında bilgi alacaksınız.

¤ Otomatik - Sohbet katılma isteklerini otomatik olarak kabul eder.

¤ Manuel - Yöneticileri etiketleyerek sohbete bir mesaj gönderilecektir. Yöneticiler, istekleri kabul edebilir veya reddedebilir.

Kullanım: /clearpending komutunu kullanarak tüm bekleyen kullanıcıları veritabanından kaldırabilirsiniz. Bu, kullanıcının tekrar istek göndermesine olanak tanır.
"""
