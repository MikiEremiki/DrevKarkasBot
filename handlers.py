import logging
import datetime
from typing import List

from telegram import (
    constants,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes, ConversationHandler

from settings import (
    CHAT_ID_FACTORY,
    CHAT_ID_SUPPLY,
    CHAT_ID_GENERAL,
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

handler_logger = logging.getLogger('bot.handler')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault('time_work', {})

    await update.effective_chat.send_message(
        'Бот готов к использованию\n'
        '/rotw - Оставить отметку Приход-Уход\n'
        '/set_my_name - Установить Имя и Фамилию для отображения в отчете\n'
        '/set_start_work - Установить время Прихода в ручную\n'
        '/set_end_work - Установить время Ухода в ручную\n'
        '/reset_time_work - Сбросить все настройки рабочего времени\n'
        '/start - Перезапустить бота\n'
    )


async def report_of_balances(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='У вас нет прав для просмотра данной информации'
        )
    else:
        report = googlesheets.balance_of_accountable_funds_report()

        if len(report[0]) == 0:
            text = 'Настройте список для отчета\nИспользуйте /config_rep_of_bal'
        else:
            text = f'#БалансСредств На текущий момент\n'
            for i in range(len(report[0])):
                text += f'{report[0][i]}: {report[1][i]}руб\n'

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=text)


async def report_of_warehouse(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.id not in [CHAT_ID_FACTORY, CHAT_ID_MIKIEREMIKI]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='У вас нет прав для просмотра данной информации'
        )
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

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=text,
                                       parse_mode=constants.ParseMode.MARKDOWN)


async def notify_assignees_morning(context: ContextTypes.DEFAULT_TYPE):
    await delete_message(
        context,
        CHAT_ID_FACTORY,
        PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT
    )
    message = await context.bot.send_message(
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
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )
    save_message_for_delete(message.message_id,
                            PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)


async def notify_assignees_evening(context: ContextTypes.DEFAULT_TYPE):
    await delete_message(
        context,
        CHAT_ID_FACTORY,
        PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT
    )
    message = await context.bot.send_message(
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
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )
    save_message_for_delete(message.message_id,
                            PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)


async def configure_report_of_balances(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='У вас нет прав для просмотра данной информации'
        )
    else:
        list_of_all_names_for_report = (
            googlesheets.get_list_of_all_names_from_sheet()
        )
        context.user_data[
            'list_of_all_names_for_report'] = list_of_all_names_for_report

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

        await update.message.reply_text(
            'Выберите кого выводить в отчете:',
            reply_markup=reply_markup
        )

        context.user_data['keyboard'] = keyboard
        context.user_data['list_name_for_report'] = list_name_for_report
        context.user_data['callback_increment'] = callback_increment

        return 1


async def generate_list_of_names(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    int_number = int(query.data)

    keyboard: List[List[InlineKeyboardButton]] = context.user_data['keyboard']
    list_name_for_report = context.user_data['list_name_for_report']
    callback_increment = context.user_data['callback_increment']
    list_of_all_names_for_report = context.user_data[
        'list_of_all_names_for_report']

    if int_number in list(range(len(list_of_all_names_for_report))):
        if keyboard[int_number][0].text.replace('✅',
                                                '') not in list_name_for_report:
            item = keyboard[int_number][0].text
            callback_data = keyboard[int_number][0].callback_data
            keyboard[int_number][0] = InlineKeyboardButton(
                f"{item}✅",
                callback_data=callback_data + callback_increment
            )
            list_name_for_report.append(
                keyboard[int_number][0].text.replace('✅', ''))

    if int_number in [callback_increment + n for n in
                      range(len(list_of_all_names_for_report))]:
        get_index_back = int_number - callback_increment

        if keyboard[get_index_back][0].text.replace('✅',
                                                    '') in list_name_for_report:
            list_name_for_report.remove(
                keyboard[get_index_back][0].text.replace('✅', ''))
        item = keyboard[get_index_back][0].text.replace('✅', '')
        keyboard[get_index_back][0] = InlineKeyboardButton(
                f"{item}",
                callback_data=get_index_back
            )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Выберите кого выводить в отчете:",
        reply_markup=reply_markup)

    context.user_data['keyboard'] = keyboard
    context.user_data['list_name_for_report'] = list_name_for_report

    write_list_of_items_in_file(list_name_for_report, PATH_LIST_NAME_FOR_REPORT)

    return 1


async def end_configure_report_of_balances(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    context_for_job = {"chat_id": query.message.chat_id,
                       "message_id": query.message.message_id}
    if query.data == 'Закрыть':
        await query.edit_message_text(
            text=f"Отчет настроен\nСообщение удалится автоматически")
        context.job_queue.run_once(delete_message_for_job_in_callback, 3,
                                   data=context_for_job)

    return ConversationHandler.END


async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '/config_rep_of_bal - настройка списка для команды /report_of_balances\n'
        'Для завершения настройки нажмите кнопку с текстом \"Закрыть\"\n\n'
        '/report_of_balances - Отчет по балансу для группы Снабжения\n'
        '/report_of_warehouse - Сводка по складу для группы Производство\n'
    )

    return 1


async def good_day(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID_GENERAL,
        text="""*_Всем позитивной работы и хорошей недели\!_*

\#СегодняМыБудемЛучшеЧемМыБылиВчера
\#НасЖдетУспех
\#TinyЗакажись
\#ФермаЗакажись
\#ГдеТоЗаказчикПытаетсяНасНайти
\#ВсеНаРаботу
\#ЯМЫКОМАНДА
\#СтаранияОкупятся""",
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )


async def nice_rest(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID_GENERAL,
        text="""*_Все молодцы, вот и прошла неделя, но нужно и отдыхать\!_*

\#СегодняМыНа\_9\_часовСталиЕщеЛучшеУмнее
\#ВОбщемКраусачики
\#НасЗасталУспех
\#ГдеТоПостроилсяTiny
\#ГдеТоИзготовиласьФерма
\#ГдеТоЗаказчикНасНашел
\#ВсеСРаботы
\#ЯМЫСПАТЬ
\#СтаранияОкупились""",
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )


async def report_of_time_work(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    handler_logger.info(f'ROTW | USER')
    handler_logger.info(update.effective_user)

    try:
        full_name = context.user_data['time_work'].get('full_name',
                                                       update.effective_user.full_name)
        text = (
            f'Ваше имя, которое будет отображаться в отчетах:\n{full_name}\n'
            'Выберите тип отметки\n\n'
            'Для настройки имени:\n'
            '/set_my_name Имя Фамилия\n'
        )
        await update.effective_chat.send_message(
            text=text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Приход', callback_data='Приход'),
                 InlineKeyboardButton('Уход', callback_data='Уход')],
            ])
        )
    except KeyError:
        await update.effective_chat.send_message(
            'Выполните команду /start'
        )


async def write_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['time_work']['type_timestamp'] = query.data
    context.user_data['time_work']['datetime_stamp'] = (datetime.datetime.now().
                                                        strftime("%d.%m.%Y %H:%M:%S"))

    await set_time_stamp(update, context)


async def set_my_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        context.user_data['time_work'][
            'full_name'] = update.effective_user.full_name
    else:
        context.user_data['time_work']['full_name'] = ' '.join(
            i for i in context.args)

    full_name = context.user_data['time_work']['full_name']
    await update.effective_chat.send_message(
        text=f'Ваше новое имя {full_name}\nДля обновления текста нажмите /rotw'
    )


async def set_start_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['time_work']['flag_start'] = True
    context.user_data['time_work']['flag_end'] = False

    datetime_stamp = ' '.join(i for i in context.args)
    datetime_stamp += ':00'  # add seconds

    try:
        context.user_data['time_work']['datetime_stamp'] = datetime_stamp
        context.user_data['time_work']['type_timestamp'] = 'Приход'

        await set_time_stamp(update, context)
    except Exception as e:
        print(e)
        await update.effective_chat.send_message(
            f'Неверный формат\nПолучилось {datetime_stamp}'
        )


async def set_end_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['time_work']['flag_start'] = True
    context.user_data['time_work']['flag_end'] = True

    datetime_stamp = ' '.join(i for i in context.args)
    datetime_stamp += ':00'  # add seconds

    try:
        context.user_data['time_work']['datetime_stamp'] = datetime_stamp
        context.user_data['time_work']['type_timestamp'] = 'Уход'

        await set_time_stamp(update, context)
    except Exception as e:
        print(e)
        await update.effective_chat.send_message(
            f'Неверный формат\nПолучилось {datetime_stamp}'
        )


async def set_time_stamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type_timestamp = context.user_data['time_work']['type_timestamp']
    full_name = context.user_data['time_work'].get('full_name',
                                                   update.effective_user.full_name)
    datetime_stamp = context.user_data['time_work']['datetime_stamp']
    flag_approve_write = False
    delta_time = '00:00'
    chat_id = update.effective_chat.id

    match type_timestamp:
        case 'Приход':
            flag_lock_start = context.user_data['time_work'].get(
                'flag_lock_start', False)
            if flag_lock_start:
                context.user_data['time_work']['flag_start'] = False
            else:
                context.user_data['time_work']['flag_start'] = True
        case 'Уход':
            context.user_data['time_work']['flag_end'] = True

    flag_start = context.user_data['time_work'].get('flag_start', None)
    flag_end = context.user_data['time_work'].get('flag_end', None)

    if flag_start and not flag_end:
        await update.effective_chat.send_message(
            'Ваша отметка:\n'
            f'Время: {datetime_stamp}\n'
            f'Тип отметки: {type_timestamp}\n'
            f'Ваше имя: {full_name}'
        )

        context.user_data['time_work'][
            'datetime_stamp_start'] = datetime.datetime.strptime(
            datetime_stamp,
            '%d.%m.%Y %H:%M:%S')
        flag_approve_write = True
        context.user_data['time_work']['flag_lock_start'] = True

    elif not flag_start and flag_end:
        await update.effective_chat.send_message(
            'Запись отклонена\n'
            'В начале необходимо сделать Приход\n'
            'Если вы забыли нажать приход, то введите время в ручную:\n'
            '/set_start_work дд.мм.гггг ч:м\n'
            'Затем повторите "Уход"'
        )

        context.user_data['time_work']['flag_end'] = False

    elif not flag_start and not flag_end:
        await update.effective_chat.send_message(
            'Запись отклонена\n'
            'Вы уже сделали Приход\n'
            'Если вы забыли нажать уход, то введите время в ручную:\n'
            '/set_end_work дд.мм.гггг ч:м\n'
            'Затем повторите "Приход"'
        )

        context.user_data['time_work']['flag_start'] = False

    elif flag_start and flag_end:
        await update.effective_chat.send_message(
            'Ваша отметка:\n'
            f'Время: {datetime_stamp}\n'
            f'Тип отметки: {type_timestamp}\n'
            f'Ваше имя: {full_name}'
        )

        context.user_data['time_work'][
            'datetime_stamp_end'] = datetime.datetime.strptime(
            datetime_stamp,
            '%d.%m.%Y %H:%M:%S')
        context.user_data['time_work']['delta_time'] = (
                context.user_data['time_work']['datetime_stamp_end'] -
                context.user_data['time_work']['datetime_stamp_start']
        )

        hours = context.user_data['time_work']['delta_time'].seconds // 3600
        minutes = context.user_data['time_work'][
                      'delta_time'].seconds // 60 % 60
        seconds = context.user_data['time_work']['delta_time'].seconds % 60
        delta_time = ':'.join([str(hours), str(minutes), str(seconds)])
        flag_approve_write = True

        context.user_data['time_work']['flag_start'] = False
        context.user_data['time_work']['flag_end'] = False
        context.user_data['time_work']['flag_lock_start'] = False

    if flag_approve_write:
        googlesheets.write_time_stamp(
            datetime_stamp,
            type_timestamp,
            full_name,
            chat_id,
            delta_time
        )


async def reset_time_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['time_work'].clear()
    await update.effective_chat.send_message(
        'Все параметры сброшены можно начать новую цепочку Приход-Уход'
    )
