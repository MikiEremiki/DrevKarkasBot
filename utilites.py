from telegram import Update
from telegram.ext import CallbackContext

from settings import CHAT_ID_FACTORY


list_message_id_for_delete = []


def delete_message(context: CallbackContext):
    if len(list_message_id_for_delete) == 2:
        context.bot.delete_message(chat_id=CHAT_ID_FACTORY,
                                   message_id=list_message_id_for_delete[0])
        list_message_id_for_delete.pop(0)


def save_message_for_delete(message_id):
    list_message_id_for_delete.append(message_id)


def echo(update: Update, context: CallbackContext):
    text = f'chat.id: {update.effective_chat.id}'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def write_list_of_items_in_file(list_of_names, path):
    with open(path, 'w', encoding='utf-8') as f:
        for item in list_of_names:
            f.write(str(item) + '\n')


def read_list_of_items_in_file(path):
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


def delete_message_for_job_in_callback(context: CallbackContext):
    context.bot.delete_message(
        chat_id=context.job.context['chat_id'],
        message_id=context.job.context['message_id']
    )
