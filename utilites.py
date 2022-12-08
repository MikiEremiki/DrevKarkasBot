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
    text = 'ECHO'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)
