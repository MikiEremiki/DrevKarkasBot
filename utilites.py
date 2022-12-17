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


def write_list_of_names_in_file(list_of_names):
    with open('list_chosen_name_for_report.txt', 'w', encoding='utf-8') as f:
        for item in list_of_names:
            f.write(item + '\n')


def read_list_of_names_in_file():
    with open('list_chosen_name_for_report.txt', mode='r', encoding='utf-8') as f:
        list_name_for_report = []
        for line in f:
            list_name_for_report.append(line.replace('\n', ''))
    return list_name_for_report


def get_list_chosen_name_for_report():
    try:
        list_name_for_report = read_list_of_names_in_file()
    except FileNotFoundError:
        list_name_for_report = []
        write_list_of_names_in_file(list_name_for_report)

    return list_name_for_report


def delete_message_for_job_in_callback(context: CallbackContext):
    context.bot.delete_message(
        chat_id=context.job.context['chat_id'],
        message_id=context.job.context['message_id']
    )
