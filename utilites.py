from telegram import Update, constants
from telegram.ext import CallbackContext
import telegram.error

import os


async def delete_message(context: CallbackContext, chat_id, path):
    list_message_id_for_delete = get_list_items_in_file(path)
    if len(list_message_id_for_delete) == 2:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=int(list_message_id_for_delete[0])
            )
        except telegram.error.BadRequest:
            print('Сообщение уже удалено')
        list_message_id_for_delete.pop(0)
        write_list_of_items_in_file(list_message_id_for_delete, path)


def save_message_for_delete(message_id, path):
    list_message_id_for_delete = get_list_items_in_file(path)
    list_message_id_for_delete.append(message_id)
    write_list_of_items_in_file(list_message_id_for_delete, path)


async def echo(update: Update, context: CallbackContext):
    text = ('chat_id = <code>' +
            str(update.effective_chat.id) + '</code>\n' +
            'user_id = <code>' +
            str(update.effective_user.id) + '</code>\n' +
            'is_forum = <code>' +
            str(update.effective_chat.is_forum) + '</code>\n' +
            'message_thread_id = <code>' +
            str(update.message.message_thread_id) + '</code>')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=constants.ParseMode.HTML
    )


def write_list_of_items_in_file(list_of_names, path):
    check_path('data')
    with open(path, 'w', encoding='utf-8') as f:
        for item in list_of_names:
            f.write(str(item) + '\n')


def read_list_of_items_in_file(path):
    check_path('data')
    with open(path, mode='r', encoding='utf-8') as f:
        list_items = []
        for line in f:
            list_items.append(line.replace('\n', ''))
    return list_items


def get_list_items_in_file(path):
    try:
        list_items = read_list_of_items_in_file(path)
    except FileNotFoundError:
        list_items = []
        write_list_of_items_in_file(list_items, path)
    return list_items


async def delete_message_for_job_in_callback(context: CallbackContext):
    await context.bot.delete_message(
        chat_id=context.job.data['chat_id'],
        message_id=context.job.data['message_id']
    )


def check_path(path):
    current_path = os.getcwd()
    path = os.path.join(current_path, path)
    if not os.path.exists(path):
        os.makedirs(path)
