# used some parts from fban.py and gban.py in Fizilion
# fban.py Copyright (C) 2020 KenHV
# gban.py Coyright (C) 2020
# created by AbOuLfOoOoOuF

import asyncio
from sqlalchemy.exc import IntegrityError
from asyncio import sleep
from userbot import CMD_HELP, bot, trgg, GBANLOG_CHATID, GBAN_ENF_CHATID, tgbott, DEVS, BOTLOG_CHATID, GBANLOG_CHATID_USER
from userbot.events import register
import userbot.modules.sql_helper.gban_sql_helper as gban_sql
from telethon.tl.types import ChatBannedRights, Channel
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditBannedRequest

fban_replies = [
    "New FedBan",
    "Starting a federation ban",
    "Start a federation ban",
    "FedBan Reason update",
    "FedBan reason updated",
    "has already been fbanned, with the exact same reason.",
]

unfban_replies = ["New un-FedBan", "I'll give", "Un-FedBan"]

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

async def admin_groups(grp):
    admgroups = []
    async for dialog in grp.client.iter_dialogs():
        entity = dialog.entity
        if (
            isinstance(entity, Channel)
            and entity.megagroup
            and (entity.creator or entity.admin_rights)
        ):
            admgroups.append(entity.id)
    return admgroups

@register(outgoing=True, disable_edited=True, pattern=r"^\{trg}execban(-d |-s | .*)(-e|-g|-f)($|-m | )(.*)".format(trg=trgg))
async def execban(event):
    # manual
    if event.pattern_match.group(3) == "-m ":
        if event.is_reply:
            return await event.edit("**Manual Ban can't be executed on a replied message**")
        else:
            if event.pattern_match.group(4):
                match = event.pattern_match.group(4)
                pattern = match.split()
                msggprf = None
                try:
                    fban_id = pattern[0]
                    reason = " ".join(pattern[1:])
                except IndexError:
                    return await event.edit("**No input given.**")
            else:    
                return await event.edit("**No input given.**")
    # reply
    if event.pattern_match.group(3) != "-m ":
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            fban_id = reply_msg.sender_id
            if event.pattern_match.group(4):
                match = event.pattern_match.group(4)
                reason = match
            else:
                reason = None
            if reply_msg:
                try:
                    msggprf = await event.client.forward_messages(GBANLOG_CHATID, reply_msg)
                except Exception:
                    pass
        else:
            return await event.edit("**Not replied to a message!**")  
    # don't gban sender or owner or dev
    if event.sender_id == fban_id or fban_id == (await event.client.get_me()).id or fban_id in DEVS:
        return await event.edit("**Permission Denied**")
    if event.pattern_match.group(2) == "-g":
        await mgban(event, fban_id, reason, msggprf)
    if event.pattern_match.group(2) == "-e":
        gcount = 0
        await gban(event, fban_id, reason, msggprf, gcount)
    if event.pattern_match.group(2) == "-f":
        gcount = 0
        await fban(event, fban_id, reason, msggprf, gcount)

async def mgban(event, fban_id, reason, msggprf):
    await sleep(1)
    if gban_sql.is_gbanned(fban_id):
        await event.client.send_message(BOTLOG_CHATID, f"`the `[user](tg://user?id={fban_id})` is already in gbanned list any way checking again`")
    else:
        gban_sql.fizgban(fban_id, reason)
    user_link = f"[{fban_id}](tg://user?id={fban_id})"
    await event.edit("getting the list of groups.")
    san = []
    san = await admin_groups(event)
    gcount = 0
    fiz = len(san)
    if fiz == 0:
        await event.client.send_message(BOTLOG_CHATID, "`you are not admin of atleast one group` ")
    else:
        await event.edit(f"**Globally Banning** {user_link} in {fiz} groups...")
        for i in range(fiz):
            try:
                await event.client(EditBannedRequest(san[i], fban_id, BANNED_RIGHTS))
                await asyncio.sleep(0.5)
                gcount += 1
            except BadRequestError:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"`You don't have required permission in :`\n**Chat :** (`{event.chat_id}`)\n`For banning here`",
                )
    await gban(event, fban_id, reason, msggprf, gcount)

async def gban(event, fban_id, reason, msggprf, gcount):
    await sleep(1)
    try:
        fban_id = await event.client.get_peer_id(fban_id)
    except Exception:
        pass
    user_link = f"[{fban_id}](tg://user?id={fban_id})"
    reason = reason if reason else "404"
    if GBAN_ENF_CHATID:
        await event.edit(f"**Executing GlobalBan** for {user_link}...")
        if msggprf != None:
            gbannn = f"!gban {user_link} {reason} // #{msggprf.id}"
        else:
            gbannn = f"!gban {user_link} {reason}"
        await event.client.send_message(GBAN_ENF_CHATID, gbannn)
    await fban(event, fban_id, reason, msggprf, gcount)

async def fban(event, fban_id, reason, msggprf, gcount):
    await sleep(1)
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
        try:
            fban_id = await event.client.get_peer_id(fban_id)
        except Exception:
            pass
        fed_list = get_flist()
        if len(fed_list) == 0:
            status = ""
            await event.client.send_message(BOTLOG_CHATID, "**You haven't connected to any federations yet!**")
        else:
            user_link = f"[{fban_id}](tg://user?id={fban_id})"
            await event.edit(f"**Executing FedBan** for {user_link}...")
            failed = []
            total = 0
            for i in fed_list:
                total += 1
                chat = int(i.chat_id)
                try:         
                    async with bot.conversation(chat) as conv:
                        if msggprf != None:
                            await conv.send_message(f"!fban {user_link} {reason} // #{msggprf.id}")
                        else:
                            await conv.send_message(f"!fban {user_link} {reason}")
                        reply = await conv.get_response()
                        if not any(i in reply.text for i in fban_replies):
                            failed.append(i.fed_name)
                except Exception:
                    failed.append(i.fed_name)
            reason = reason if reason else "404"
            if failed:
                status = f"\n**Feds Affected:** {total} \n**Failed in:** {len(failed)}\n"
                for i in failed:
                    status += f"--  {i}\n"
            else:
                status = f"\n**Feds Affected:** {total}"
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")
    await banlog(event, fban_id, reason, msggprf, gcount, user_link, status, total) 

async def banlog(event, fban_id, reason, msggprf, gcount, user_link, status, total):
    await sleep(1)
    sender = await event.get_sender()
    sender_link = f"[{sender.id}](tg://user?id={sender.id})"
    reason = reason if reason else "404"
    if user_link:
        user_link = user_link
    else: 
        user_link = fban_id
    # messages
    if event.pattern_match.group(2) == "-g":
        enforced_ban_string = f"#ENFORCED\n**Global Ban**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nBan Reason: {reason}\nFeds Affected = {total}\nGban Status = Enforced\nManual GBan = True\nGroups Affected = {gcount}"
        donemsg = f"#GlobalBan\n**Target User** = {user_link}!\n**Ban Reason:** {reason}\n**Feds Affected:** {status}\n**Bots Affected:** 7\n**Manual Actions:**\n**Banned in:** {status} **Groups**"
    if event.pattern_match.group(2) == "-e":
        enforced_ban_string = f"#ENFORCED\n**GBan**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nBan Reason: {reason}\nFeds Affected = {total}\nGban Status = Enforced"
        donemsg = f"#FedBan\n**Target User** = {user_link}!\n**Ban Reason:** {reason}\n**Feds Affected:** {status}\n**Bots Affected:** 7"
    if event.pattern_match.group(2) == "-f":
        enforced_ban_string = f"#ENFORCED\nFedBan\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nBan Reason: {reason}\nFeds Affected: {total}"
        donemsg = f"#GBan\n**Target User** = {user_link}!\n**Ban Reason:** {reason}\n**Feds Affected:** {status}"
    # log
    if msggprf != None:
        enforced_ban_string += f"\n--------------\nMessage Count: #[{msggprf.id}](https://t.me/c/{GBANLOG_CHATID_USER}/{msggprf.id})"
        donemsg += f"\n--------------\nMessage Count: #[{msggprf.id}](https://t.me/c/{GBANLOG_CHATID_USER}/{msggprf.id})"
    await tgbott.send_message(GBANLOG_CHATID, enforced_ban_string)
    await event.edit(donemsg)
    if event.pattern_match.group(1) == "-s ":
        await sleep(2)
        try:
            await event.delete()
        except Exception:
            pass
    if event.pattern_match.group(1) == "-d ":
        if event.is_reply:
            try:
                await sleep(2)
                await event.get_reply_message.delete()
            except Exception:
                pass
        else:
            pass 

##############################################################################################################################

@register(outgoing=True, disable_edited=True, pattern=r"^\{trg}revert(-s | .*)(-e|-g|-f)($|-m | )(.*)".format(trg=trgg))
async def rexecban(event):
    match = event.pattern_match.group(4)
    # manual
    if event.pattern_match.group(3) == "-m ":
        if event.is_reply:
            return await event.edit("**Manual Ban can't be executed on a replied message**")
        else:
            if event.pattern_match.group(4):
                match = event.pattern_match.group(4)
                pattern = match.split()
                msggprf = None
                try:
                    fban_id = pattern[0]
                    reason = " ".join(pattern[1:])
                except IndexError:
                    return await event.edit("**No input given.**")
            else:    
                return await event.edit("**No input given.**")
    # reply
    if event.pattern_match.group(3) != "-m ":
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            fban_id = reply_msg.sender_id
            if event.pattern_match.group(4):
                match = event.pattern_match.group(4)
                reason = match
            else:
                reason = None
            if reply_msg:
                try:
                    msggprf = await event.client.forward_messages(GBANLOG_CHATID, reply_msg)
                except Exception:
                    pass
        else:
            return await event.edit("**Not replied to a message!**")    
    # don't gban sender or owner or dev
    if event.sender_id == fban_id or fban_id == (await event.client.get_me()).id or fban_id in DEVS:
        await event.edit("**User shouldn't be banned, reverting anyway in 3 seconds.**")
        await sleep(3)
    if event.pattern_match.group(2) == "-g":
        await rmgban(event, fban_id, reason, msggprf)
    if event.pattern_match.group(2) == "-e":
        gcount = 0
        await rgban(event, fban_id, reason, msggprf, gcount)
    if event.pattern_match.group(2) == "-f":
        gcount = 0
        await rfban(event, fban_id, reason, msggprf, gcount)

async def rmgban(event, fban_id, reason, msggprf):
    await sleep(1)
    if gban_sql.is_gbanned(fban_id):
        await event.client.send_message(BOTLOG_CHATID, f"`the `[user](tg://user?id={fban_id})` is already in gbanned list any way checking again`")
    else:
        gban_sql.fizgban(fban_id, reason)
    user_link = f"[{fban_id}](tg://user?id={fban_id})"
    await event.edit("getting the list of groups.")
    san = []
    san = await admin_groups(event)
    gcount = 0
    fiz = len(san)
    if fiz == 0:
        await event.client.send_message(BOTLOG_CHATID, "`you are not admin of atleast one group` ")
    else:
        await event.edit(f"**Globally UnBanning** {user_link} in {fiz} groups...")
        for i in range(fiz):
            try:
                await event.client(EditBannedRequest(san[i], fban_id, UNBAN_RIGHTS))
                await asyncio.sleep(0.5)
                gcount += 1
            except BadRequestError:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"`You don't have required permission in :`\n**Chat :** (`{event.chat_id}`)\n`For banning here`",
                )
    await rgban(event, fban_id, reason, msggprf, gcount)

async def rgban(event, fban_id, reason, msggprf, gcount):
    await sleep(1)
    try:
        fban_id = await event.client.get_peer_id(fban_id)
    except Exception:
        pass
    user_link = f"[{fban_id}](tg://user?id={fban_id})"
    reason = reason if reason else "404"
    if GBAN_ENF_CHATID:
        await event.edit(f"**Reverting GlobalBan** for {user_link}...")
        if msggprf != None:
            gbannn = f"!ungban {user_link} {reason} // #{msggprf.id}"
        else:
            gbannn = f"!ungban {user_link} {reason}"
        await event.client.send_message(GBAN_ENF_CHATID, gbannn)
    await rfban(event, fban_id, reason, msggprf, gcount)

async def rfban(event, fban_id, reason, msggprf, gcount):
    await sleep(1)
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
        try:
            fban_id = await event.client.get_peer_id(fban_id)
        except Exception:
            pass
        fed_list = get_flist()
        if len(fed_list) == 0:
            status = ""
            await event.client.send_message(BOTLOG_CHATID, "**You haven't connected to any federations yet!**")
        else:
            user_link = f"[{fban_id}](tg://user?id={fban_id})"
            await event.edit(f"**Reverting FedBan** for {user_link}...")
            failed = []
            total = 0
            for i in fed_list:
                total += 1
                chat = int(i.chat_id)
                try:         
                    async with bot.conversation(chat) as conv:
                        if msggprf != None:
                            await conv.send_message(f"!unfban {user_link} {reason} // #{msggprf.id}")
                        else:
                            await conv.send_message(f"!unfban {user_link} {reason}")
                        reply = await conv.get_response()
                        if not any(i in reply.text for i in fban_replies):
                            failed.append(i.fed_name)
                except Exception:
                    failed.append(i.fed_name)
            reason = reason if reason else "404"
            if failed:
                status = f"\n**Feds Affected:** {total} \n**Failed in:** {len(failed)}\n"
                for i in failed:
                    status += f"--  {i}\n"
            else:
                status = f"\n**Feds Affected:** {total}"
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")
    await rbanlog(event, fban_id, reason, msggprf, gcount, user_link, status, total) 

async def rbanlog(event, fban_id, reason, msggprf, gcount, user_link, status, total):
    await sleep(1)
    sender = await event.get_sender()
    sender_link = f"[{sender.id}](tg://user?id={sender.id})"
    reason = reason if reason else "404"
    if user_link:
        user_link == user_link
    else:
        user_link == fban_id
    # messages
    if event.pattern_match.group(2) == "-g":
        enforced_ban_string = f"#REVERTED\n**Global Ban**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nUnBan Reason: {reason}\nFeds Affected = {total}\nGban Status = Reverted\nManual UnGBan = True\nGroups Affected = {gcount}"
        donemsg = f"#Revert_GlobalBan\n**Target User** = {user_link}!\n**UnBan Reason:** {reason}\n**Feds Affected:** {status}\n**Bots Affected:** 7\n**Manual Actions:**\n**Banned in:** {status} **Groups**"
    if event.pattern_match.group(2) == "-e":
        enforced_ban_string = f"#REVERTED\n**GBan**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nUnBan Reason: {reason}\nFeds Affected = {total}\nGban Status = Reverted"
        donemsg = f"#Revert_FedBan\n**Target User** = {user_link}!\n**UnBan Reason:** {reason}\n**Feds Affected:** {status}\n**Bots Affected:** 7"
    if event.pattern_match.group(2) == "-f":
        enforced_ban_string = f"#REVERTED\nFedBan\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nUnBan Reason: {reason}\nFeds Affected: {total}"
        donemsg = f"#Revert_GBan\n**Target User** = {user_link}!\n**UnBan Reason:** {reason}\n**Feds Affected:** {status}"
    # log
    if msggprf != None:
        enforced_ban_string += f"\n--------------\nMessage Count: #[{msggprf.id}](https://t.me/c/{GBANLOG_CHATID}/{msggprf.id})"
        donemsg += f"\n--------------\nMessage Count: #[{msggprf.id}](https://t.me/c/{GBANLOG_CHATID}/{msggprf.id})"
    await tgbott.send_message(GBANLOG_CHATID, enforced_ban_string.format(sender_link=sender_link, user_link=user_link, reason=reason, total=total))
    await event.edit(donemsg)
    if event.pattern_match.group(1) == "-s":
        await sleep(2)
        try:
            await event.delete()
        except Exception:
            pass


CMD_HELP.update(
    {
        "bans": ">`{trgg}execban <args>`"
        "\nargs are:(-d |-s | .*)(-e|-g|-f)($|-m | )(.*)<id/username> <reason>"
        "\nUsage: Ban user."
        "\nUser can be banned from connected Federations, Group bots, and where the sender is admin, depending on the passed args."
        "\nYou can reply to the user whom you want to ban or manually pass the username/id with the required args."
        "\nMake sure to set it up correctly or it won't work."
        "\n>`{trgg}revert <args>`"
        "\nargs are:(-s | .*)(-e|-g|-f)($|-m | )(.*)<id/username> <reason>"
        "\nUsage: Reverts the execban."
        "\nUser can be unbanned from connected Federations, Group bots, and where the sender is admin, depending on the passed args."
        "\nYou can reply to the user whom you want to unban or manually pass the username/id with the required args."
        "\nMake sure to set it up correctly or it won't work."
    }
)


