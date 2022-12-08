from telegram import constants, Update
from telegram.ext import CallbackContext

from settings import CHAT_ID_FACTORY, CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI
import googlesheets
from utilites import delete_message, save_message_for_delete


def report_of_balances(update: Update, context: CallbackContext):
    if update.effective_chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='У вас нет прав для просмотра данной информации')
    else:
        report = googlesheets.balance_of_accountable_funds_report()

        text = f'#БалансСредств На текущий момент\n'
        for i in range(len(report[0])):
            text += f'{report[0][i]}: {report[1][i]}руб\n'

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text)


def report_of_warehouse(update: Update, context: CallbackContext):
    if update.effective_chat.id not in [CHAT_ID_FACTORY, CHAT_ID_MIKIEREMIKI]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='У вас нет прав для просмотра данной информации')
    else:
        report = googlesheets.balance_of_warehouse_report()

        text = f'#БалансСклада\n'
        for key_1, item in report.items():
            text += f'\n*{key_1} ({item["Дата"]}):*\n'
            text += f'Доска:\n'
            for key_2, value in item['Доска'].items():
                text += f'{key_2}: {value}\n'
            text += f'\nПластины:\n'
            text += f'{item["Пластины"]}\n'

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 parse_mode=constants.PARSEMODE_MARKDOWN)


def notify_assignees_morning(context: CallbackContext):
    delete_message(context)
    response = context.bot.send_message(
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
    save_message_for_delete(response['message_id'])


def notify_assignees_evening(context: CallbackContext):
    delete_message(context)
    response = context.bot.send_message(
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
    save_message_for_delete(response['message_id'])
