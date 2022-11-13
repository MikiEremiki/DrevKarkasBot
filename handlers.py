from telegram import constants, Update
from telegram.ext import CallbackContext

from settings import CHAT_ID_FACTORY, CHAT_ID_SUPPLY
import googlesheets


def echo(update: Update, context: CallbackContext):
    text = 'ECHO:'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def report(update: Update, context: CallbackContext):
    list_for_report = googlesheets.main()

    text = f'#БалансСредств На текущий момент\n'
    for i in range(len(list_for_report[0])):
        text += f'{list_for_report[0][i]}: {list_for_report[1][i]}руб\n'

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def notify_assignees_morning(context: CallbackContext):
    context.bot.send_message(
        chat_id=CHAT_ID_FACTORY,
        text="""*_Напоминание

Что сейчас в работе?_*

Пишем с большой буквы
\#Отгрузка
\#Перепиловка
\#Приемка
\#Ревизия
\#Сдача
\#Замена
\#Вработу
\#Отчет""",
        parse_mode=constants.PARSEMODE_MARKDOWN_V2
    )


def notify_assignees_evening(context: CallbackContext):
    context.bot.send_message(
        chat_id=CHAT_ID_FACTORY,
        text="""*_Напоминание

Проверьте, что ничего не забыли написать за день_*

Пишем с большой буквы
\#Отгрузка
\#Перепиловка
\#Приемка
\#Ревизия
\#Сдача
\#Замена
\#Вработу
\#Отчет""",
        parse_mode=constants.PARSEMODE_MARKDOWN_V2
    )
