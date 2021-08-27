# Copyright (C) 2021 AbOuLfOoOoOuF

from userbot import CMD_HELP, trgg, tgbott, bot
from userbot.events import botregister


@botregister(pattern=f"^\{trgg}echo($| .*)")
async def echoo(event):
    chat = event.chat_id
    entity = await tgbott.get_entity(chat)
    if entity.default_banned_rights.send_messages: 
        return
    else:
        if event.is_reply:
            echoo = await event.get_reply_message()
        else:
            echoo = event.pattern_match.group(1)
        if echoo:
            await event.delete()
            await tgbott.send_message(chat, echoo)
        else:
            await event.delete()

@botregister(pattern="/start")
async def startt(event):
    chat = event.chat_id
    me = await bot.get_me()
    startstr = f"Hello, this is Forkzilion and I'm [{me.first_name}](tg://user?id={me.id})'s assistant.\nIf ur interested in deploying this bot go to [Forkzilion repo](github.com/AbOuLfOoOoOuF/ProjectFizilionFork)."
    await tgbott.send_message(chat, startstr, link_preview=False)

CMD_HELP.update(
    {
        "bot": f">`{trgg}echo`"
        "\necho"
    }
)