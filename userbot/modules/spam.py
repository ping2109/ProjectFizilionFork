# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

import asyncio
from asyncio import sleep

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, trgg, tgbott
from userbot.events import register


@register(outgoing=True, pattern="^\{trg}cspam (.*)".format(trg=trgg))
async def leter_spam(cspammer):
    try:
        cspam = str(cspammer.pattern_match.group(1))
    except ValueError:
        return
    message = cspam.replace(" ", "")
    await cspammer.delete()
    for letter in message:
        await cspammer.respond(letter)
    if BOTLOG:
        await tgbott.send_message(
            BOTLOG_CHATID, "#CSPAM\n" "TSpam was executed successfully"
        )


@register(outgoing=True, pattern="^\{trg}wspam (.*)".format(trg=trgg))
async def word_spam(wspammer):
    try:
        wspam = str(wspammer.pattern_match.group(1))
    except ValueError:
        return
    message = wspam.split()
    await wspammer.delete()
    for word in message:
        await wspammer.respond(word)
    if BOTLOG:
        await tgbott.send_message(
            BOTLOG_CHATID, "#WSPAM\n" "WSpam was executed successfully"
        )


@register(outgoing=True, pattern="^\{trg}spam (.*)".format(trg=trgg))
async def spammer(spamm):
    try:
        counter = int(spamm.pattern_match.group(1).split(" ", 1)[0])
    except IndexError:
        await spamm.edit("The usage of this command is .spam <count> <text> or .spam <count> replyiing to a message")
        await sleep(5)
        await spamm.delete()
        return
    textx = await spamm.get_reply_message()
    if not textx:
        try:
            spam_message = str(spamm.pattern_match.group(1).split(" ", 1)[1])
        except IndexError:
            await spamm.edit("The usage of this command is .spam <count> <text> or .spam <count> replyiing to a message")
            await sleep(5)
            await spamm.delete()
            return
        await spamm.delete()
        await asyncio.wait([spamm.respond(spam_message) for i in range(counter)])
        if BOTLOG:
            await tgbott.send_message(
                BOTLOG_CHATID, "#SPAM\n" "Spam was executed successfully"
            )
    elif (textx and textx.text):
        await spamm.delete()
        await asyncio.wait([spamm.respond(textx) for i in range(counter)])
        if BOTLOG:
            await tgbott.send_message(
                BOTLOG_CHATID, "#SPAM\n" "Spam was executed successfully"
            )

@register(outgoing=True, pattern="^\{trg}rp$".format(trg=trgg))
async def repeattt(event):
    textx = await event.get_reply_message()
    await event.delete()
    await event.respond(textx)

@register(outgoing=True, pattern="^\{trg}drp$".format(trg=trgg))
async def drepeattt(event):
    textx = await event.get_reply_message()
    await event.delete()
    try:
        await textx.delete()
    except Exception:
        pass
    await event.respond(textx)

@register(outgoing=True, pattern="^\{trg}picspam".format(trg=trgg))
async def tiny_pic_spam(pspam):
    message = pspam.text
    text = message.split()
    try:
        counter = int(text[1])
        link = str(text[2])
    except IndexError:
        await pspam.edit("The usage of this command is .picspam <count> <link to image/gif>")
        await sleep(5)
        await pspam.delete()
        return
    await pspam.delete()
    for _ in range(1, counter):
        await pspam.client.send_file(pspam.chat_id, link)
    if BOTLOG:
        await tgbott.send_message(
            BOTLOG_CHATID, "#PICSPAM\n" "PicSpam was executed successfully"
        )


@register(outgoing=True, pattern="^\{trg}delayspam (.*)".format(trg=trgg))
async def dspammer(dspam):
    try:
        spamDelay = float(dspam.pattern_match.group(1).split(" ", 2)[0])
        counter = int(dspam.pattern_match.group(1).split(" ", 2)[1])
        spam_message = str(dspam.pattern_match.group(1).split(" ", 2)[2])
    except IndexError:
        await dspam.edit("The usage of this command is .delayspam <delay> <count> <text>")
        await sleep(5)
        await dspam.delete()
        return
    await dspam.delete()
    for _ in range(1, counter):
        await dspam.respond(spam_message)
        await sleep(spamDelay)
    if BOTLOG:
        await tgbott.send_message(
            BOTLOG_CHATID, "#DelaySPAM\n" "DelaySpam was executed successfully"
        )


CMD_HELP.update(
    {
        "spam": ".cspam <text>\
\nUsage: Spam the text letter by letter.\
\n\n.spam <count> <text>\
\nUsage: Floods text in the chat !!\
\n\n.rp\
\nUsage: Repeats the replied message!!\
\n\n.drp\
\nUsage: Repeats the replied message and deletes the main one!!\
\n\n.wspam <text>\
\nUsage: Spam the text word by word.\
\n\n.picspam <count> <link to image/gif>\
\nUsage: As if text spam was not enough !!\
\n\n.delayspam <delay> <count> <text>\
\nUsage: .bigspam but with custom delay.\
\n\n\nNOTE : Spam at your own risk !!"
    }
)