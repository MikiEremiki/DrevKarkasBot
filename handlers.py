import logging
import datetime
import asyncio
from typing import List, Dict

from aiogram import Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton, ReplyKeyboardRemove
)
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from settings import (
    CHAT_ID_FACTORY,
    CHAT_ID_SUPPLY,
    CHAT_ID_GENERAL,
    CHAT_ID_MIKIEREMIKI,
    PATH_LIST_NAME_FOR_REPORT,
    PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT, TOPIC_ID_FACTORY_REPORT
)
import googlesheets
from utilites import (
    delete_message,
    save_message_for_delete,
    get_list_items_in_file,
    write_list_of_items_in_file
)


class ConfigReportStates(StatesGroup):
    waiting_for_selection = State()


handler_logger = logging.getLogger('bot.handler')


async def start(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'time_work' not in data:
        await state.update_data(time_work={})

    await message.answer(
        'Бот готов к использованию\n'
        '/rotw - Оставить отметку Приход-Уход\n'
        '/set_my_name - Установить Имя и Фамилию для отображения в отчете\n'
        '/set_start_work - Установить время Прихода в ручную\n'
        '/set_end_work - Установить время Ухода в ручную\n'
        '/reset_time_work - Сбросить все настройки рабочего времени\n'
        '/start - Перезапустить бота\n',
        reply_markup=ReplyKeyboardRemove()
    )


async def report_of_balances(message: Message):
    if message.chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        await message.answer('У вас нет прав для просмотра данной информации')
    else:
        report = await googlesheets.balance_of_accountable_funds_report()

        if len(report[0]) == 0:
            text = 'Настройте список для отчета\nИспользуйте /config_rep_of_bal'
        else:
            text = f'#БалансСредств На текущий момент\n'
            for i in range(len(report[0])):
                text += f'{report[0][i]}: {report[1][i]}руб\n'

        await message.answer(text)


async def report_of_warehouse(message: Message):
    if message.chat.id not in [CHAT_ID_FACTORY, CHAT_ID_MIKIEREMIKI]:
        await message.answer('У вас нет прав для просмотра данной информации')
    else:
        report = await googlesheets.balance_of_warehouse_report()

        text = f'#БалансСклада\n'
        for key_1, item in report.items():
            text += f'\n*{key_1} ({item["Дата"]}):*\n'
            text += f'Доска:\n'
            for key_2, value in item['Доска'].items():
                text += f'{key_2}: {value}\n'
            text += f'\nПластины:\n'
            text += f'{item["Пластины"]}\n'

        await message.answer(text, parse_mode=ParseMode.MARKDOWN)


async def notify_assignees_morning(bot: Bot):
    await delete_message(
        bot,
        CHAT_ID_FACTORY,
        PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT
    )

    text = (
        'Напоминание\n'
        '\n'
        '<b><i>Что сейчас в работе?</i></b>\n'
        '\n'
        'Пишем с большой буквы\n'
        '#Отгрузка\n'
        '#Перепиловка\n'
        '#Приемка\n'
        '#Ревизия\n'
        '#Сдача\n'
        '#Замена\n'
        '#Вработу\n'
        '#Отчет\n'
    )
    message = await bot.send_message(
        chat_id=CHAT_ID_FACTORY,
        text=text,
        message_thread_id=TOPIC_ID_FACTORY_REPORT
    )
    save_message_for_delete(message.message_id,
                            PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)


async def notify_assignees_evening(bot: Bot):
    await delete_message(
        bot,
        CHAT_ID_FACTORY,
        PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT
    )

    text = (
        'Напоминание'
        '\n\n'
        '<b><i>Проверьте, что ничего не забыли написать за день</i></b>'
        '\n\n'
        'Пишем с большой буквы\n'
        '#Отгрузка\n'
        '#Перепиловка\n'
        '#Приемка\n'
        '#Ревизия\n'
        '#Сдача\n'
        '#Замена\n'
        '#Вработу\n'
        '#Отчет\n'
    )
    message = await bot.send_message(
        chat_id=CHAT_ID_FACTORY,
        text=text,
        message_thread_id=TOPIC_ID_FACTORY_REPORT
    )
    save_message_for_delete(message.message_id,
                            PATH_LIST_MESSAGE_FOR_DELETE_IN_FACTORY_CHAT)


async def configure_report_of_balances(
        message: Message, state: FSMContext):
    if message.chat.id not in [CHAT_ID_SUPPLY, CHAT_ID_MIKIEREMIKI]:
        await message.answer('У вас нет прав для просмотра данной информации')
    else:
        list_of_all_names_for_report = (
            await googlesheets.get_list_of_all_names_from_sheet()
        )

        list_name_for_report = get_list_items_in_file(PATH_LIST_NAME_FOR_REPORT)

        callback_increment = 10 * len(str(len(list_name_for_report)))

        # Create keyboard
        buttons = []
        for i, item in enumerate(list_of_all_names_for_report):
            display_item = item
            callback_data = str(i)

            if item in list_name_for_report:
                display_item += '✅'
                callback_data = str(i + callback_increment)

            buttons.append([
                InlineKeyboardButton(text=display_item,
                                     callback_data=callback_data)
            ])

        buttons.append([
            InlineKeyboardButton(text="Закрыть", callback_data='Закрыть')
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            'Выберите кого выводить в отчете:',
            reply_markup=keyboard
        )

        await state.update_data(
            list_of_all_names_for_report=list_of_all_names_for_report,
            keyboard_buttons=buttons,
            list_name_for_report=list_name_for_report,
            callback_increment=callback_increment
        )

        await state.set_state(ConfigReportStates.waiting_for_selection)


async def help_command(message: Message):
    await message.answer(
        '/config_rep_of_bal - настройка списка для команды /report_of_balances\n'
        'Для завершения настройки нажмите кнопку с текстом \"Закрыть\"\n\n'
        '/report_of_balances - Отчет по балансу для группы Снабжения\n'
        '/report_of_warehouse - Сводка по складу для группы Производство\n'
    )


async def delete_message_after_delay(bot: Bot, context_data: Dict,
                                     delay: int = 3):
    """Delete a message after a specified delay in seconds"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(
            chat_id=context_data["chat_id"],
            message_id=context_data["message_id"]
        )
    except Exception as e:
        handler_logger.error(f"Error deleting message: {e}")


async def good_day(bot: Bot):
    text = (
        '<b><i>Всем позитивной работы и хорошей недели!</i></b>'
        '\n\n'
        '#СегодняМыБудемЛучшеЧемМыБылиВчера\n'
        '#НасЖдетУспех\n'
        '#TinyЗакажись\n'
        '#ФермаЗакажись\n'
        '#ГдеТоЗаказчикПытаетсяНасНайти\n'
        '#ВсеНаРаботу\n'
        '#ЯМЫКОМАНДА\n'
        '#СтаранияОкупятся\n'
    )
    await bot.send_message(
        chat_id=CHAT_ID_GENERAL,
        text=text
    )


async def nice_rest(bot: Bot):
    text = (
        '<b><i>Все молодцы, вот и прошла неделя, но нужно и отдыхать!</i></b>'
        '\n\n'
        '#СегодняМыНа_9_часовСталиЕщеЛучшеУмнее\n'
        '#ВОбщемКраусачики\n'
        '#НасЗасталУспех\n'
        '#ГдеТоПостроилсяTiny\n'
        '#ГдеТоИзготовиласьФерма\n'
        '#ГдеТоЗаказчикНасНашел\n'
        '#ВсеСРаботы\n'
        '#ЯМЫСПАТЬ\n'
        '#СтаранияОкупились\n'
    )
    await bot.send_message(
        chat_id=CHAT_ID_MIKIEREMIKI,
        text=text
    )


async def report_of_time_work(message: Message, state: FSMContext):
    handler_logger.info(f'ROTW | USER')
    handler_logger.info(message.from_user)

    try:
        data = await state.get_data()
        time_work = data.get('time_work', {})
        full_name = time_work.get('full_name', message.from_user.full_name)

        text = (
            f'Ваше имя, которое будет отображаться в отчетах:\n{full_name}\n'
            'Выберите тип отметки\n\n'
            'Для настройки имени:\n'
            '/set_my_name Имя Фамилия\n'
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Приход', callback_data='Приход'),
                InlineKeyboardButton(text='Уход', callback_data='Уход')
            ]
        ])

        await message.answer(text=text, reply_markup=keyboard)
    except Exception as e:
        handler_logger.error(f"Error in report_of_time_work: {e}")
        await message.answer('Выполните команду /start')


async def write_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    time_work = data.get('time_work', {})

    time_work['type_timestamp'] = callback.data
    datetime_stamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    time_work['datetime_stamp'] = datetime_stamp

    await state.update_data(time_work=time_work)

    await set_time_stamp(callback.message, state)


async def set_my_name(message: Message, state: FSMContext):
    data = await state.get_data()
    time_work = data.get('time_work', {})

    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if len(args) == 0:
        time_work['full_name'] = message.from_user.full_name
    else:
        time_work['full_name'] = ' '.join(args)

    await state.update_data(time_work=time_work)

    full_name = time_work['full_name']
    text = f'Ваше новое имя {full_name}\nДля обновления текста нажмите /rotw'
    await message.answer(text)


async def set_start_work(message: Message, state: FSMContext):
    data = await state.get_data()
    time_work = data.get('time_work', {})

    time_work['flag_start'] = True
    time_work['flag_end'] = False

    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    datetime_stamp = ' '.join(args)
    datetime_stamp += ':00'  # add seconds

    try:
        time_work['datetime_stamp'] = datetime_stamp
        time_work['type_timestamp'] = 'Приход'

        await state.update_data(time_work=time_work)
        await set_time_stamp(message, state)
    except Exception as e:
        handler_logger.error(f"Error in set_start_work: {e}")
        await message.answer(
            f'Неверный формат\nПолучилось {datetime_stamp}'
        )


async def set_end_work(message: Message, state: FSMContext):
    data = await state.get_data()
    time_work = data.get('time_work', {})

    time_work['flag_start'] = True
    time_work['flag_end'] = True

    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    datetime_stamp = ' '.join(args)
    datetime_stamp += ':00'  # add seconds

    try:
        time_work['datetime_stamp'] = datetime_stamp
        time_work['type_timestamp'] = 'Уход'

        await state.update_data(time_work=time_work)
        await set_time_stamp(message, state)
    except Exception as e:
        handler_logger.error(f"Error in set_end_work: {e}")
        await message.answer(
            f'Неверный формат\nПолучилось {datetime_stamp}'
        )


async def set_time_stamp(
        message: Message,
        state: FSMContext,
):
    data = await state.get_data()
    time_work = data.get('time_work', {})

    type_timestamp = time_work.get('type_timestamp', '')
    full_name = time_work.get('full_name', message.from_user.full_name)
    datetime_stamp = time_work.get('datetime_stamp', '')
    flag_approve_write = False
    delta_time = '00:00'
    chat_id = message.chat.id

    match type_timestamp:
        case 'Приход':
            flag_lock_start = time_work.get('flag_lock_start', False)
            if flag_lock_start:
                time_work['flag_start'] = False
            else:
                time_work['flag_start'] = True
        case 'Уход':
            time_work['flag_end'] = True

    flag_start = time_work.get('flag_start', None)
    flag_end = time_work.get('flag_end', None)

    if flag_start and not flag_end:
        await message.answer(
            'Ваша отметка:\n'
            f'Время: {datetime_stamp}\n'
            f'Тип отметки: {type_timestamp}\n'
            f'Ваше имя: {full_name}'
        )

        time_work['datetime_stamp_start'] = datetime.datetime.strptime(
            datetime_stamp, '%d.%m.%Y %H:%M:%S')
        flag_approve_write = True
        time_work['flag_lock_start'] = True

    elif not flag_start and flag_end:
        await message.answer(
            'Запись отклонена\n'
            'В начале необходимо сделать Приход\n'
            'Если вы забыли нажать приход, то введите время в ручную:\n'
            '/set_start_work дд.мм.гггг ч:м\n'
            'Затем повторите "Уход"'
        )

        time_work['flag_end'] = False

    elif not flag_start and not flag_end:
        await message.answer(
            'Запись отклонена\n'
            'Вы уже сделали Приход\n'
            'Если вы забыли нажать уход, то введите время в ручную:\n'
            '/set_end_work дд.мм.гггг ч:м\n'
            'Затем повторите "Приход"'
        )

        time_work['flag_start'] = False

    elif flag_start and flag_end:
        await message.answer(
            'Ваша отметка:\n'
            f'Время: {datetime_stamp}\n'
            f'Тип отметки: {type_timestamp}\n'
            f'Ваше имя: {full_name}'
        )

        time_work['datetime_stamp_end'] = datetime.datetime.strptime(
            datetime_stamp, '%d.%m.%Y %H:%M:%S')
        time_work['delta_time'] = (
                time_work['datetime_stamp_end'] -
                time_work['datetime_stamp_start']
        )

        hours = time_work['delta_time'].seconds // 3600
        minutes = time_work['delta_time'].seconds // 60 % 60
        seconds = time_work['delta_time'].seconds % 60
        delta_time = ':'.join([str(hours), str(minutes), str(seconds)])
        flag_approve_write = True

        time_work['flag_start'] = False
        time_work['flag_end'] = False
        time_work['flag_lock_start'] = False

    await state.update_data(time_work=time_work)

    if flag_approve_write:
        await googlesheets.write_time_stamp(
            datetime_stamp,
            type_timestamp,
            full_name,
            chat_id,
            delta_time
        )


async def reset_time_work(message: Message, state: FSMContext):
    # Reset time_work data
    await state.update_data(time_work={})

    await message.answer(
        'Все параметры сброшены можно начать новую цепочку Приход-Уход'
    )
