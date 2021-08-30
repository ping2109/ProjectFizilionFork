# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for managing events.
 One of the main components of the userbot. """

import sys
from asyncio import create_subprocess_shell as asyncsubshell
from asyncio import subprocess as asyncsub
from os import remove
from time import gmtime, strftime
from traceback import format_exc
import time 
from telethon import events, errors
from userbot import LOGSPAMMER, BOTLOG_CHATID, bot, tgbott, assistant


def register(**args):
    """ Register a new event. """
    pattern = args.get('pattern', None)
    disable_edited = args.get('disable_edited', False)
    ignore_unsafe = args.get('ignore_unsafe', False)
    unsafe_pattern = r'^[^/!#@\*$A-Za-z]'
    groups_only = args.get('groups_only', False)
    trigger_on_fwd = args.get('trigger_on_fwd', False)
    disable_errors = args.get('disable_errors', False)
    insecure = args.get('insecure', False)

    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern

    if "disable_edited" in args:
        del args['disable_edited']

    if "ignore_unsafe" in args:
        del args['ignore_unsafe']

    if "groups_only" in args:
        del args['groups_only']

    if "disable_errors" in args:
        del args['disable_errors']

    if "trigger_on_fwd" in args:
        del args['trigger_on_fwd']

    if "insecure" in args:
        del args['insecure']

    if pattern:
        if not ignore_unsafe:
            args['pattern'] = pattern.replace('^.', unsafe_pattern, 1)

    def decorator(func):
        async def wrapper(check):
            if check.edit_date and check.is_channel and not check.is_group:
                # Messages sent in channels can be edited by other users.
                # Ignore edits that take place in channels.
                return
            if not LOGSPAMMER:
                check.chat_id
            else:
                pass

            if not trigger_on_fwd and check.fwd_from:
                return

            if groups_only and not check.is_group:
                await check.respond("`I don't think this is a group.`")
                return

            if check.via_bot_id and not insecure and check.out:
                return

            try:
                await func(check)

            except errors.FloodWaitError as fw:
                await tgbott.send_message(BOTLOG_CHATID, f"`Umm, we have an issue...:\nA flood wait error has been raised.\n{str(fw)}\n\nI will sleep for a bit.`")
                time.sleep(fw.seconds)
                await tgbott.send_message(BOTLOG_CHATID, "`I'm back online!`")


            # Thanks to @kandnub for this HACK.
            # Raise StopPropagation to Raise StopPropagation
            # This needed for AFK to working properly

            except events.StopPropagation:
                raise events.StopPropagation
            # This is a gay exception and must be passed out. So that it doesnt
            # spam chats
            except KeyboardInterrupt:
                pass
            except BaseException:

                # Check if we have to disable it.
                # If not silence the log spam on the console,
                # with a dumb except.

                if not disable_errors:
                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                    text = "**USERBOT ERROR REPORT**\n"
                    text += "Umm an issue happened and it's been logged here.\n"
                    text += "Nothing is logged except the fact of error and date\n"

                    ftext = "========== DISCLAIMER =========="
                    ftext += "\nAlready know it...\nError and date are logged.\n"
                    ftext += "================================\n\n"
                    ftext += "--------BEGIN USERBOT TRACEBACK LOG--------\n"
                    ftext += "\nDate: " + date
                    ftext += "\nChat ID: " + str(check.chat_id)
                    ftext += "\nSender ID: " + str(check.sender_id)
                    ftext += "\n\nEvent Trigger:\n"
                    ftext += str(check.text)
                    ftext += "\n\nTraceback info:\n"
                    ftext += str(format_exc())
                    ftext += "\n\nError text:\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "\n\n--------END USERBOT TRACEBACK LOG--------"

                    command = "git log --pretty=format:\"%an: %s\" -10"

                    ftext += "\n\n\nLast 10 commits:\n"

                    process = await asyncsubshell(command,
                                                  stdout=asyncsub.PIPE,
                                                  stderr=asyncsub.PIPE)
                    stdout, stderr = await process.communicate()
                    result = str(stdout.decode().strip()) \
                        + str(stderr.decode().strip())

                    ftext += result

                    file = open("error.log", "w+")
                    file.write(ftext)
                    file.close()

                    txtt = "Umm an issue has ocurred...\n\n"
                    txtt += "Chat: " + str(check.chat_id)
                    txtt += "\n\nErr: " + str(sys.exc_info()[1])

                    if LOGSPAMMER:
                        await tgbott.send_message(BOTLOG_CHATID, txtt)
                        await tgbott.send_file(BOTLOG_CHATID, "error.log", caption=text)                   
                    else: 
                        await tgbott.send_message('me', txtt)
                        await check.client.send_file(BOTLOG_CHATID, "error.log", caption=text)               
                    remove("error.log")
            else:
                pass

        if not disable_edited:
            bot.add_event_handler(wrapper, events.MessageEdited(**args))
        bot.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper

    return decorator

def regassist(**args):
    """ Register a new event. """
    pattern = args.get('pattern', None)
    disable_edited = args.get('disable_edited', False)
    ignore_unsafe = args.get('ignore_unsafe', False)
    unsafe_pattern = r'^[^/!#@\*$A-Za-z]'
    groups_only = args.get('groups_only', False)
    trigger_on_fwd = args.get('trigger_on_fwd', False)
    disable_errors = args.get('disable_errors', False)
    insecure = args.get('insecure', False)
    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern
    if "disable_edited" in args:
        del args['disable_edited']
    if "ignore_unsafe" in args:
        del args['ignore_unsafe']
    if "groups_only" in args:
        del args['groups_only']
    if "disable_errors" in args:
        del args['disable_errors']
    if "trigger_on_fwd" in args:
        del args['trigger_on_fwd']
    if "insecure" in args:
        del args['insecure']
    if pattern:
        if not ignore_unsafe:
            args['pattern'] = pattern.replace('^.', unsafe_pattern, 1)
    def decorator(func):
        async def wrapper(check):
            if check.edit_date and check.is_channel and not check.is_group:
                return
            if not LOGSPAMMER:
                check.chat_id
            else:
                pass
            if not trigger_on_fwd and check.fwd_from:
                return

            if groups_only and not check.is_group:
                await check.respond("`I don't think this is a group.`")
                return
            if check.via_bot_id and not insecure and check.out:
                return
            try:
                await func(check)
            except errors.FloodWaitError as fw:
                await bot.send_message(BOTLOG_CHATID, f"`Umm, we have an issue...:\nA flood wait error has been raised.\n{str(fw)}\n\nI will sleep for a bit.`")
                time.sleep(fw.seconds)
                await bot.send_message(BOTLOG_CHATID, "`I'm back online!`")
            # credits are given in the previous occurrence a few lines ago
            except events.StopPropagation:
                raise events.StopPropagation
            except KeyboardInterrupt:
                pass
            except BaseException:
                if not disable_errors:
                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    text = "**USERBOT ERROR REPORT**\n"
                    text += "Umm an issue happened and it's been logged here.\n"
                    text += "Nothing is logged except the fact of error and date\n"
                    ftext = "========== DISCLAIMER =========="
                    ftext += "\nAlready know it...\nError and date are logged.\n"
                    ftext += "================================\n\n"
                    ftext += "--------BEGIN USERBOT TRACEBACK LOG--------\n"
                    ftext += "\nDate: " + date
                    ftext += "\nChat ID: " + str(check.chat_id)
                    ftext += "\nSender ID: " + str(check.sender_id)
                    ftext += "\n\nEvent Trigger:\n"
                    ftext += str(check.text)
                    ftext += "\n\nTraceback info:\n"
                    ftext += str(format_exc())
                    ftext += "\n\nError text:\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "\n\n--------END USERBOT TRACEBACK LOG--------"
                    command = "git log --pretty=format:\"%an: %s\" -10"
                    ftext += "\n\n\nLast 10 commits:\n"
                    process = await asyncsubshell(command,
                                                  stdout=asyncsub.PIPE,
                                                  stderr=asyncsub.PIPE)
                    stdout, stderr = await process.communicate()
                    result = str(stdout.decode().strip()) \
                        + str(stderr.decode().strip())
                    ftext += result
                    file = open("error.log", "w+")
                    file.write(ftext)
                    file.close()
                    txtt = "Umm an issue has ocurred...\n\n"
                    txtt += "Chat: " + str(check.chat_id)
                    txtt += "\n\nErr: " + str(sys.exc_info()[1])
                    if LOGSPAMMER:
                        await tgbott.send_message(BOTLOG_CHATID, txtt)
                        await tgbott.send_file(BOTLOG_CHATID, "error.log", caption=text)
                    else: 
                        await tgbott.send_message('me', txtt)
                        await check.client.send_file(BOTLOG_CHATID, "error.log", caption=text)
                    remove("error.log")
            else:
                pass
        if not disable_edited:
            assistant.add_event_handler(wrapper, events.MessageEdited(**args))
        assistant.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper
    return decorator
