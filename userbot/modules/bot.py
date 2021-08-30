# Copyright (C) 2021 AbOuLfOoOoOuF

from userbot import CMD_HELP, trgg, bot, OWNER_ID, tgbott, BOTLOG_CHATID
from userbot.events import regassist
from telethon import Button, errors
from asyncio import sleep

@regassist(pattern=f"^\{trgg}echo($| .*)")
async def echoo(event):
    if event.sender.id is OWNER_ID:
        return
    else:
        if event.is_reply:
            echoo = await event.get_reply_message()
        else:
            echoo = event.pattern_match.group(1)
        if echoo:
            await event.delete()
            await event.respond(echoo)
        else:
            await event.delete()

@regassist(pattern="/start$")
async def startt(event):
    me = await bot.get_me()
    if event.sender.id != me.id:
        await event.reply("Hewwo")
    else:
        if event.is_group and event.is_channel:
            return
        else:
            try:
                startstr = f"Hello, this is Forkzilion and I'm [{me.first_name}](tg://user?id={me.id})'s assistant.\nIf ur interested in deploying this bot, check out the button below."
                strtbtn = [(Button.url("Repo", "https://github.com/AbOuLfOoOoOuF/ProjectFizilionFork"))]
                await event.respond(startstr, buttons=strtbtn, link_preview=False)
            except errors.FloodWaitError as fw:
                dumb = f"[{event.sender.first_name}](tg://user?id={event.sender.id})"
                msg = f"This idiot {dumb} is spamming your bot and caused it to hit flood limit.\nError:\n{fw}"
                await tgbott.send_message(BOTLOG_CHATID, msg)

CMD_HELP.update(
    {
        "bot": f">`{trgg}echo`"
        "\necho"
    }
)