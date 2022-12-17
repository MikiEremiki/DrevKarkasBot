from telegram import constants, Update
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler

from settings import (
    CHAT_ID_FACTORY,
    CHAT_ID_SUPPLY,
    CHAT_ID_MIKIEREMIKI,
    PATH_LIST_NAME_FOR_REPORT,
    PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT
)
import googlesheets
from utilites import (
    delete_message,
    save_message_for_delete,
    delete_message_for_job_in_callback,
    get_list_items_in_file,
    write_list_of_items_in_file
)


def report_of_balances(update: Update, context: CallbackContext):
    if update.effective_chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='У вас нет прав для просмотра данной информации')
    else:
        report = googlesheets.balance_of_accountable_funds_report()

        if len(report[0]) == 0:
            text = 'Настройте список для отчета\nИспользуйте /configure'
        else:
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
    delete_message(context, CHAT_ID_FACTORY, PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)
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
    save_message_for_delete(response['message_id'], PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)


def notify_assignees_evening(context: CallbackContext):
    delete_message(context, CHAT_ID_FACTORY, PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)
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
    save_message_for_delete(response['message_id'], PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)


def configure_report_of_balances(update: Update, context: CallbackContext):
    if update.effective_chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='У вас нет прав для просмотра данной информации')
    else:
        list_of_all_names_for_report = googlesheets.get_list_of_all_names_from_sheet()
        context.user_data['list_of_all_names_for_report'] = list_of_all_names_for_report

        list_name_for_report = get_list_items_in_file(PATH_LIST_NAME_FOR_REPORT)

        callback_increment = 10 * len(str(len(list_name_for_report)))
        keyboard = []
        for i, item in enumerate(list_of_all_names_for_report):
            if item in list_name_for_report:
                item += '✅'
                i += callback_increment

            button_tmp = InlineKeyboardButton(
                f"{item}",
                callback_data=i
            )
            keyboard.append([button_tmp])

        button_tmp = InlineKeyboardButton(
            "Закрыть",
            callback_data='Закрыть'
        )
        keyboard.append([button_tmp])

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Выберите кого выводить в отчете:', reply_markup=reply_markup)

        context.user_data['keyboard'] = keyboard
        context.user_data['list_name_for_report'] = list_name_for_report
        context.user_data['callback_increment'] = callback_increment

        return 1


def generate_list_of_names(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    int_number = int(query.data)

    keyboard = context.user_data['keyboard']
    list_name_for_report = context.user_data['list_name_for_report']
    callback_increment = context.user_data['callback_increment']
    list_of_all_names_for_report = context.user_data['list_of_all_names_for_report']

    if int_number in list(range(len(list_of_all_names_for_report))):
        if keyboard[int_number][0].text.replace('✅', '') not in list_name_for_report:
            keyboard[int_number][0].text += '✅'
            keyboard[int_number][0].callback_data += callback_increment
            list_name_for_report.append(keyboard[int_number][0].text.replace('✅', ''))

    if int_number in [callback_increment + n for n in range(len(list_of_all_names_for_report))]:
        get_index_back = int_number - callback_increment

        if keyboard[get_index_back][0].text.replace('✅', '') in list_name_for_report:
            list_name_for_report.remove(keyboard[get_index_back][0].text.replace('✅', ''))
        keyboard[get_index_back][0].text = keyboard[get_index_back][0].text.replace('✅', '')
        keyboard[get_index_back][0].callback_data = get_index_back

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Выберите кого выводить в отчете:", reply_markup=reply_markup)

    context.user_data['keyboard'] = keyboard
    context.user_data['list_name_for_report'] = list_name_for_report

    write_list_of_items_in_file(list_name_for_report, PATH_LIST_NAME_FOR_REPORT)

    return 1


def end_configure_report_of_balances(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context_for_job = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}
    if query.data == 'Закрыть':
        query.edit_message_text(text=f"Отчет настроен\nСообщение удалится автоматически")
        context.job_queue.run_once(delete_message_for_job_in_callback, 3, context=context_for_job)

    return ConversationHandler.END


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        "/config_rep_of_bal - настройка списка для команды /report_of_balances\n"
        "Для завершения настройки нажмите кнопку с текстом \"Закрыть\"\n\n"
        "/report_of_balances - Отчет по балансу для группы Снабжения\n"
        "/report_of_warehouse - Сводка по складу для группы Производство\n"
    )

    return 1
