#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telepot
import time
import os
from datetime import datetime
from functions_all import logwrite, save_vars, load_vars  # load and save variables
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton  # telegram keyboard

token = ''  # platryatest_bot token
TelegramBot = telepot.Bot(token)
send_message = TelegramBot.sendMessage
log_filename = 'logs/telegram_mirvn.txt'
var_dump_filename = 'data/telegram_mirvn.pickle'

startmessage = u'Список тегов. Кликните чтобы подписаться/отписаться (+/-). Чтобы ещё раз вывести теги на экран введите или кликните /showtags.'
helpmessage = startmessage


def create_keyboard(chat_id):  # create keyboard for telegram
    keyboard = list()
    for tag in all_tags:
        if tag in storage[chat_id]:  # add + or - to button name
            tag_comment = ' +'
        else:
            tag_comment = ' -'
        keyboard.append([InlineKeyboardButton(text=tag + tag_comment, callback_data=tag)])  # add button to keyboard
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def find_tags(text):  # find tags in tags. That is after #.
    tags = list()
    for i in text.split():
        if i[0] == '#' and 1 < len(i) < 20:  # if first symbol is # and it is not long and not empty.
            tags.append(i[1:])
            if i[1:] not in all_tags:
                all_tags.append(i[1:])  # add tag to all available tags
                save_vars(var_dump_filename, storage, all_tags)
    return tags


def send_by_tag(tags, text):  # send message to everybody subscribed to tag
    for tag in tags:
        for key, value in storage.items():
            if tag in value:
                send_message(key, text)


def on_callback_query(msg):  # if button in telegram is pressed
    message_id = msg['message']['message_id']  # just for keyboard editing
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['message']['chat']['id']
    logwrite(var_dump_filename, str(datetime.now())[:-4], chat_id, query_data)
    if chat_id not in storage:
        storage[chat_id] = list()

    if query_data not in storage[chat_id]:  # add or remove tag for user
        storage[chat_id].append(query_data)
    elif query_data in storage[chat_id]:
        storage[chat_id].remove(query_data)

    save_vars(var_dump_filename, storage, all_tags)

    keyboard = create_keyboard(chat_id)  # create keyboard
    TelegramBot.editMessageReplyMarkup((chat_id, message_id), reply_markup=keyboard)  # edit keyboard. replaces + or - in button text.


def on_chat_message(msg):
    if __name__ != '__main__':
        return
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        return
    text = msg['text']
    logwrite(var_dump_filename, str(datetime.now())[:-4], chat_id, msg['text'])
    if chat_id not in storage:
        storage[chat_id] = list()

    if chat_id == -1001144468367:  # if chat is Mirvn
        tags = find_tags(text)  # find tags in message
        send_by_tag(tags, text)  # send message to subscribed users
        return

    elif text.lower() == 'start' or text == '/start':
        keyboard = create_keyboard(chat_id)
        send_message(chat_id, startmessage, reply_markup=keyboard)  # send start message if "/start" pressed

    elif text.lower() == '/help' or text == 'help':
        TelegramBot.sendMessage(chat_id, helpmessage)

    elif text.lower() == 'st':
        print 'storage = ', storage
        print 'all tags = ', all_tags
        send_message(chat_id, str(storage) + '\n' + str(all_tags))

    elif text.lower() == 'showtags' or text == '/showtags':
        keyboard = create_keyboard(chat_id)
        send_message(chat_id, 'Tags:', reply_markup=keyboard)

    elif text[:10] == 'delete_tag':
        tag = text[11:]
        all_tags.remove(tag)
        send_message(chat_id, tag + ' removed')

# storage = {123456: ['pv', 'ev'], 789321: [u'ВИЭ', 'shale']}  # storage example. two users with two tags each

storage = dict()
all_tags = list()

if os.path.isfile(var_dump_filename):  # load variables
    storage, all_tags = load_vars(var_dump_filename)

TelegramBot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})  # receive bot messages
print ('Listening ...')
while 1:  # Keep the program running.
    time.sleep(10)
