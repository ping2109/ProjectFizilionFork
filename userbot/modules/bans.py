# used some parts from fban.py and gban.py in Fizilion
# fban.py Copyright (C) 2020 KenHV
# gban.py Coyright (C) 2020
# created by AbOuLfOoOoOuF

import asyncio
from sqlalchemy.exc import IntegrityError
from asyncio import sleep
from userbot import CMD_HELP, bot, trgg, GBANLOG_CHATID, GBAN_ENF_CHATID, tgbott, DEVS, BOTLOG_CHATID, GBANLOG_CHATID_USER, TIMEOUT
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


@register(outgoing=True, disable_edited=True, pattern=r"^\{trg}(exec|auto)ban(-d |-s |-i | .*)(-e|-g|-f)($|-m | )(.*)".format(trg=trgg))
async def execban(event):
    await event.edit("Ban initiated...")
    # manual
    if event.pattern_match.group(4) == "-m ":
        if event.is_reply:
            return await event.edit("**Manual Ban can't be executed on a replied message**")
        else:
            if event.pattern_match.group(5):
                match = event.pattern_match.group(5)
                pattern = match.split()
                msggprf = None
                try:
                    fban_id = pattern[0]
                    reason = " ".join(pattern[1:])
                    if reason:
                        reason = reason
                    else:
                        reason = "Not specified"
                except IndexError:
                    return await event.edit("**No input given.**")

            else:    
                return await event.edit("**No input given.**")
    # reply
    if event.pattern_match.group(4) != "-m ":
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            fban_id = reply_msg.sender_id
            if event.pattern_match.group(5):
                match = event.pattern_match.group(5)
                reason = match
            else:
                reason = "Not specified"
            if reply_msg:
                try:
                    msggprf = await event.client.forward_messages(GBANLOG_CHATID, reply_msg)

                    if event.pattern_match.group(2) == "-i ":
                        try:
                            await event.delete()
                        except Exception as er:
                            await tgbott.send_message(BOTLOG_CHATID, str(er))
                            await event.reply("An error has ocurred, check logs for more info.")
                            pass
                        try:
                            await event.delete()
                        except Exception as er:
                            await tgbott.send_message(BOTLOG_CHATID, str(er))
                            await event.reply("An error has ocurred, check logs for more info.")
                            pass
                    if event.pattern_match.group(2) == "-d ":
                        try:
                            await reply_msg.delete()
                        except Exception as er:
                            await tgbott.send_message(BOTLOG_CHATID, str(er))
                            await event.reply("An error has ocurred, check logs for more info.")
                            pass

                except Exception as err:
                    await tgbott.send_message(BOTLOG_CHATID, str(err))
                    await event.reply("An error has ocurred, check logs for more info.")
                    pass
        else:
            return await event.edit("**Not replied to a message!**")  
    # don't gban sender or owner or dev
    if event.sender_id == fban_id or fban_id == (await event.client.get_me()).id or fban_id in DEVS:
        return await event.edit("**Permission Denied**")
    # autoreason
    if event.pattern_match.group(1) == "exec":
        #await event.edit(reason)
        await banexec(event, fban_id, reason, msggprf)
    elif event.pattern_match.group(1) == "auto":
        await autoreason(event, fban_id, reason, msggprf)

async def autoreason(event, fban_id, areason, msggprf):
    if areason == "btc":
        reason = "0xSPAM <auto detected> match on bitcoin."
    elif areason == "bot":
        reason = "0xSPAM <auto detected> spambot."
    elif areason == "spambot":
        reason = "0xSPAM <auto detected> spambot."
    elif areason == "spam bot":
        reason = "0xSPAM <auto detected> spambot."
    elif areason == "crypto":
        reason = "0xSPAM <auto detected> match on crypto."
    elif areason == "scam":
        reason = "0xSPAM <auto detected scam>."
    elif areason == "earn":
        reason = "0xSPAM <auto detected> match on earn."
    elif areason == "trading":
        reason = "0xSPAM <auto detected> match on trade-trading."
    elif areason == "spam":
        reason = "0xSPAM <auto detected>"

    elif areason.startswith("spam "):
        rsn = areason.partition("spam ")[2]
        reason = f"0xSPAM <auto detected> // {rsn}"
    elif areason.startswith("scam "):
        rsn = areason.partition("scam ")[2]
        reason = f"0xSPAM <auto detected> // {rsn}"
###################
    elif areason == "pm":
        reason = "0xPUP <auto detected> pm spammer."
    elif areason == "leaker":
        reason = "0xPUP <auto detected> leaker"
    elif areason == "leak":
        reason = "0xPUP <auto detected> leak"
    elif areason == "pup":
        reason = r"0xPUP <auto detected>"

    elif areason.startswith("pup "):
        rsn = areason.partition("pup ")[2]
        reason = f"0xPUP <auto detected> // {rsn}"
###################
    elif areason == "+18":
        reason = "0xNSFW <auto detected> +18 bot."
    elif areason == "nsfw":
        reason = "0xNSFW <auto detected> nsfw bot."

    elif areason.startswith("nsfw "):
        rsn = areason.partition("nsfw ")[2]
        reason = f"0xNSFW <auto detected> // {rsn}."
###################
    elif areason == "alt":
        reason = "0xEVADE <auto detected> alt"
    elif areason == "evade":
        reason = "0xEVADE <auto detected> evading ban"

    elif areason.startswith("evade "):
        rsn = areason.partition("evade ")[2]
        reason = f"0xEVADE <auto detected> // {rsn}"
###################
    elif areason == "imper":
        reason = "0xIMPER <auto detected> impersonator"

    elif areason.startswith("imper "):
        rsn = areason.partition("imper ")[2]
        reason = f"0xIMPER <auto detected> // {rsn}"
###################
    elif areason == "raid":
        reason = "0xRAID <auto detected>"

    elif areason.startswith("raid "):
        rsn = areason.partition("raid ")[2]
        reason = f"0xRAID <auto detected> // {rsn}"
###################
    elif areason == "-":
        reason = "0x0 <null>"

    elif areason == "x":
        reason = "0x? <no input>"


    elif areason.startswith("-r "):
        reasonn = areason.partition("-r ")[2]
        try:
            rsnn = reasonn.partition(" ")[0].upper()
            rsn = reasonn.partition(" ")[2]
            reason = f"0x{rsnn} // {rsn}"
        except Exception:
            reason = "0x? <no input>"

    elif areason == "404":
        reason = "0x? <no input>"
    elif areason == "Not specified":
        reason = "Not specified"

    elif areason.startswith("-o "):
        reasonn = areason.partition("-o ")[2]
        try:
            rsn = reasonn.partition(" ")[2]
            reason = f"0xOTHER // {rsn}"
        except Exception:
            reason = "0x? <no input>"

    else:
        reason = "0xOTHER // "
        reason += areason

    #await event.edit(reason)
    await banexec(event, fban_id, reason, msggprf)

async def banexec(event, fban_id, reason, msggprf):
    if event.pattern_match.group(3) == "-g":
        await mgban(event, fban_id, reason, msggprf)
    if event.pattern_match.group(3) == "-e":
        gcount = 0
        await gban(event, fban_id, reason, msggprf, gcount)
    if event.pattern_match.group(3) == "-f":
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
    if GBAN_ENF_CHATID:
        await event.edit(f"**Executing GlobalBan** for {user_link}...")
        if msggprf != None:
            if reason == "Not specified":
                gbannn = f"!gban {user_link} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
            elif reason != "Not specified":
                gbannn = f"!gban {user_link} {reason} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
        else:
            if reason == "Not specified":
                gbannn = f"!gban {user_link}"
            elif reason != "Not specified":
                gbannn = f"!gban {user_link} {reason}"
        await event.client.send_message(GBAN_ENF_CHATID, gbannn, link_preview=False)
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
                            if reason == "Not specified":
                                await conv.send_message(f"!fban {user_link} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})", link_preview=False)
                            elif reason != "Not specified":
                                await conv.send_message(f"!fban {user_link} {reason} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})", link_preview=False)
                        else:
                            if reason == "Not specified":
                                await conv.send_message(f"!fban {user_link}")
                            if reason != "Not specified":
                                await conv.send_message(f"!fban {user_link} {reason}")

                        reply = await conv.get_response()
                        if not any(i in reply.text for i in fban_replies):
                            failed.append(i.fed_name)
                except Exception:
                    failed.append(i.fed_name)
            if failed:
                status = f"\n**Feds Affected:** {total} \n**Failed in:** {len(failed)}\n"
                for i in failed:
                    statuss = f"--  {i}\n"
            else:
                status = f"\n**Feds Affected:** {total}"
                statuss = ""
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")
    await event.edit(reason + "\n" + status + "\n" + statuss)
    await sleep(5)
    await banlog(event, fban_id, reason, msggprf, gcount, user_link, status, statuss, total) 

async def banlog(event, fban_id, reason, msggprf, gcount, user_link, status, statuss, total):
    await sleep(1)
    sender = await event.get_sender()
    sender_link = f"[{sender.id}](tg://user?id={sender.id})"
    if user_link:
        user_link = user_link
    else: 
        user_link = fban_id

    staatuss = status + statuss

    # messages
    if event.pattern_match.group(3) == "-g":
        enforced_ban_string = f"#ENFORCED\n**Global Ban**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nBan Reason: {reason}\n**Feds Affected** = {total}\n**Gban Status** = `Enforced`\n**Manual GBan** = `True`\n**Groups Affected** = {gcount}"
        donemsg = f"#GlobalBan\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n{statuss}\n**Bots Affected:** 7\n**Manual Actions:**\n**Banned in:** {gcount} **Groups**"
    if event.pattern_match.group(3) == "-e":
        enforced_ban_string = f"#ENFORCED\n**GBan**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n**Feds Affected** = {total}\n**Failed in:** {status}\n**Gban Status** = `Enforced`"
        donemsg = f"#GBan\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n{staatuss}\n**Bots Affected:** 7"
    if event.pattern_match.group(3) == "-f":
        enforced_ban_string = f"#ENFORCED\nFedBan\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n**Feds Affected:** {total}"
        donemsg = f"#FedBan\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n{staatuss}"
    # log
    if msggprf != None:
        enforced_ban_string += f"\n----------------------\nMessage Count: #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
        donemsg += f"\n----------------------\nMessage Count: #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
    await tgbott.send_message(GBANLOG_CHATID, enforced_ban_string, link_preview=False)
    await event.edit(donemsg)

    if event.pattern_match.group(2) == "-s ":
        await sleep(2)
        try:
            await event.delete()
        except Exception as er:
            await tgbott.send_message(BOTLOG_CHATID, str(er))
            await event.reply("An error has ocurred, check logs for more info.")
            pass
    if event.pattern_match.group(2) == "-i ":
        await sleep(2)
        try:
            await event.delete()
        except Exception as er:
            await tgbott.send_message(BOTLOG_CHATID, str(er))
            await event.reply("An error has ocurred, check logs for more info.")
            pass

    await tgbott.send_message(BOTLOG_CHATID, "Event Complete! --" + event.pattern_match.group(1) + " -" + event.pattern_match.group(2) + "-" + event.pattern_match.group(3) + " -" + event.pattern_match.group(4))

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################



@register(outgoing=True, disable_edited=True, pattern=r"^\{trg}(revert|autorevert)(-d |-s |-i | .*)(-e|-g|-f)($|-m | )(.*)".format(trg=trgg))
async def unexecban(event):
    await event.edit("Ban initiated...")
    # manual
    if event.pattern_match.group(4) == "-m ":
        if event.is_reply:
            return await event.edit("**Manual Ban can't be executed on a replied message**")
        else:
            if event.pattern_match.group(5):
                match = event.pattern_match.group(5)
                pattern = match.split()
                msggprf = None
                try:
                    fban_id = pattern[0]
                    reason = " ".join(pattern[1:])
                    if reason:
                        reason = reason
                    else:
                        reason = "Not specified"
                except IndexError:
                    return await event.edit("**No input given.**")

            else:    
                return await event.edit("**No input given.**")
    # reply
    if event.pattern_match.group(4) != "-m ":
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            fban_id = reply_msg.sender_id
            if event.pattern_match.group(5):
                match = event.pattern_match.group(5)
                reason = match
            else:
                reason = "Not specified"
            if reply_msg:
                try:
                    msggprf = await event.client.forward_messages(GBANLOG_CHATID, reply_msg)

                except Exception as err:
                    await tgbott.send_message(BOTLOG_CHATID, str(err))
                    await event.reply("An error has ocurred, check logs for more info.")
                    pass
        else:
            return await event.edit("**Not replied to a message!**")  
    # don't gban sender or owner or dev
    if event.sender_id == fban_id or fban_id == (await event.client.get_me()).id or fban_id in DEVS:
        return await event.edit("**Permission Denied**")
    # autoreason
    if event.pattern_match.group(1) == "revert":
        #await event.edit(reason)
        await unbanexec(event, fban_id, reason, msggprf)
    elif event.pattern_match.group(1) == "autorevert":
        await unautoreason(event, fban_id, reason, msggprf)

async def unautoreason(event, fban_id, areason, msggprf):

    if areason == "-":
        reason = "0x0 <null>"

    elif areason == "x":
        reason = "0x? <no input>"


    elif areason.startswith("-r "):
        reasonn = areason.partition("-r ")[2]
        try:
            rsnn = reasonn.partition(" ")[0].upper()
            rsn = reasonn.partition(" ")[2]
            reason = f"0x{rsnn} // {rsn}"
        except Exception:
            reason = "0x? <no input>"

    elif areason == "404":
        reason = "0x? <no input>"
    elif areason == "Not specified":
        reason = "Not specified"

    elif areason.startswith("-o "):
        reasonn = areason.partition("-o ")[2]
        try:
            rsn = reasonn.partition(" ")[2]
            reason = f"0xOTHER // {rsn}"
        except Exception:
            reason = "0x? <no input>"

    else:
        reason = "0xOTHER // "
        reason += areason

    #await event.edit(reason)
    await unbanexec(event, fban_id, reason, msggprf)

async def unbanexec(event, fban_id, reason, msggprf):
    if event.pattern_match.group(3) == "-g":
        await unmgban(event, fban_id, reason, msggprf)
    if event.pattern_match.group(3) == "-e":
        gcount = 0
        await ungban(event, fban_id, reason, msggprf, gcount)
    if event.pattern_match.group(3) == "-f":
        gcount = 0
        await unfban(event, fban_id, reason, msggprf, gcount)

async def unmgban(event, fban_id, reason, msggprf):
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
                    f"`You don't have required permission in :`\n**Chat :** (`{event.chat_id}`)\n`For unbanning here`",
                )
    await ungban(event, fban_id, reason, msggprf, gcount)

async def ungban(event, fban_id, reason, msggprf, gcount):
    await sleep(1)
    try:
        fban_id = await event.client.get_peer_id(fban_id)
    except Exception:
        pass
    user_link = f"[{fban_id}](tg://user?id={fban_id})"
    if GBAN_ENF_CHATID:
        await event.edit(f"**Reverting GlobalBan** for {user_link}...")
        if msggprf != None:
            if reason == "Not specified":
                gbannn = f"!ungban {user_link} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
            elif reason != "Not specified":
                gbannn = f"!ungban {user_link} {reason} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
        else:
            if reason == "Not specified":
                gbannn = f"!ungban {user_link}"
            elif reason != "Not specified":
                gbannn = f"!ungban {user_link} {reason}"
        await event.client.send_message(GBAN_ENF_CHATID, gbannn, link_preview=False)
    await unfban(event, fban_id, reason, msggprf, gcount)

async def unfban(event, fban_id, reason, msggprf, gcount):
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
                            if reason == "Not specified":
                                await conv.send_message(f"!unfban {user_link} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})", link_preview=False)
                            elif reason != "Not specified":
                                await conv.send_message(f"!unfban {user_link} {reason} // #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})", link_preview=False)
                        else:
                            if reason == "Not specified":
                                await conv.send_message(f"!unfban {user_link}")
                            if reason != "Not specified":
                                await conv.send_message(f"!unfban {user_link} {reason}")

                        reply = await conv.get_response()
                        if not any(i in reply.text for i in fban_replies):
                            failed.append(i.fed_name)
                except Exception:
                    failed.append(i.fed_name)
            if failed:
                status = f"\n**Feds Affected:** {total} \n**Failed in:** {len(failed)}\n"
                for i in failed:
                    statuss = f"--  {i}\n"
            else:
                status = f"\n**Feds Affected:** {total}"
                statuss = ""
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")
    await event.edit(reason + "\n" + status + "\n" + statuss)
    await sleep(5)
    await unbanlog(event, fban_id, reason, msggprf, gcount, user_link, status, statuss, total) 

async def unbanlog(event, fban_id, reason, msggprf, gcount, user_link, status, statuss, total):
    await sleep(1)
    sender = await event.get_sender()
    sender_link = f"[{sender.id}](tg://user?id={sender.id})"
    if user_link:
        user_link = user_link
    else: 
        user_link = fban_id

    staatuss = status + statuss

    # messages
    if event.pattern_match.group(3) == "-g":
        enforced_ban_string = f"#REVERT\n**Global Ban**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\nBan Reason: {reason}\n**Feds Affected** = {total}\n**Gban Status** = `Reverted`\n**Manual GBan** = `True`\n**Groups Affected** = {gcount}"
        donemsg = f"#UnGlobalBan\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n{statuss}\n**Bots Affected:** 7\n**Manual Actions:**\n**Banned in:** {gcount} **Groups**"
    if event.pattern_match.group(3) == "-e":
        enforced_ban_string = f"#REVERT\n**GBan**\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n**Feds Affected** = {total}\n**Failed in:** {status}\n**Gban Status** = `Reverted`"
        donemsg = f"#UnGBan\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n{staatuss}\n**Bots Affected:** 7"
    if event.pattern_match.group(3) == "-f":
        enforced_ban_string = f"#REVERT\nFedBan\n**Enforcer** = {sender_link}\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n**Feds Affected:** {total}"
        donemsg = f"#UnFedBan\n**Target User** = {user_link}\n**Ban Reason:** {reason}\n{staatuss}"
    # log
    if msggprf != None:
        enforced_ban_string += f"\n----------------------\nMessage Count: #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
        donemsg += f"\n----------------------\nMessage Count: #[{msggprf.id}](https://t.me/{GBANLOG_CHATID_USER}/{msggprf.id})"
    await tgbott.send_message(GBANLOG_CHATID, enforced_ban_string, link_preview=False)
    await event.edit(donemsg)

    if event.pattern_match.group(2) == "-s ":
        await sleep(2)
        try:
            await event.delete()
        except Exception as er:
            await tgbott.send_message(BOTLOG_CHATID, str(er))
            await event.reply("An error has ocurred, check logs for more info.")
            pass
    if event.pattern_match.group(2) == "-i ":
        await sleep(2)
        try:
            await event.delete()
        except Exception as er:
            await tgbott.send_message(BOTLOG_CHATID, str(er))
            await event.reply("An error has ocurred, check logs for more info.")
            pass

    await tgbott.send_message(BOTLOG_CHATID, "Event Complete! --" + event.pattern_match.group(1) + " -" + event.pattern_match.group(2) + "-" + event.pattern_match.group(3) + " -" + event.pattern_match.group(4))






@register(outgoing=True, pattern="^\{trg}bantags$".format(trg=trgg))
async def bantags(event):
    await event.edit("List of tags used in bans:\n`0xSPAM`  -  `0xPUP`  -  `0xNSFW`  -  `0xEVADE`  -  `0xIMPER`  -  `0xRAID`  -  `0x0``  -  `0x?`  -  `0xOTHER`")
    await sleep(30)
        
    if TIMEOUT:
        await event.delete() 


@register(outgoing=True, pattern="^\{trg}banstr$".format(trg=trgg))
async def banstr(event):
    await event.edit(
        "\n\n0xSPAM"
        "\nbtc, bot, spambot, spam bot, crypto, scam, earn, trading, spam, spam .*, scam .*"
        "\n\n0xPUP"
        "\npm, leaker, leak, pup, pup .*"
        "\n\n0xNSFW"
        "\n+18, nsfw, nsfw .*"
        "\n\n0xEVADE"
        "\nalt, evade, evade .*"
        "\n\n0xIMPER"
        "\nimper, imper .*"
        "\n\n0xRAID"
        "\nraid, raid .*"
        "\n\n0x0 "
        "\n-"
        "\n\n0x?"
        "\nx"
        "\n-o"
        "\n\n0xOTHER"
        "\n-r str"
        "\n\n0xSTR"
    )
    await sleep(30)
        
    if TIMEOUT:
        await event.delete()


CMD_HELP.update(
    {
        "bans": f">`{trgg}execban<args>`"
        f"\n>`{trgg}autoban<args>`"
        f"\n\nargs are:(-d |-s |-i | .*)(-e|-g|-f)($|-m | )(.*)<id/username> <reason>"
        f"\nautoban uses a detected reason (if it exists)"
        f"\nUsage: Ban user."
        f"\nUser can be banned from connected Federations, Group bots, and where the sender is admin, depending on the passed args."
        f"\nYou can reply to the user whom you want to ban or manually pass the username/id with the required args."
        f"\nMake sure to set it up correctly or it won't work."
        f"\n\n>`{trgg}revert <args>`"
        f"\n\>`{trgg}autorevert <args>`"
        f"\nargs are:(-s |-i | .*)(-e|-g|-f)($|-m | )(.*)<id/username> <reason>"
        f"\nautorevert uses a detected reason (if it exists)"
        f"\nUsage: Reverts the execban."
        f"\nUser can be unbanned from connected Federations, Group bots, and where the sender is admin, depending on the passed args."
        f"\nYou can reply to the user whom you want to unban or manually pass the username/id with the required args."
        f"\nMake sure to set it up correctly or it won't work."
    }

)

CMD_HELP.update(
    {
        "bantags": f">`{trgg}bantags`"
        "\nshow the list of tags used in bans --  meaning added soon"
    }
)