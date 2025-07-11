import asyncio
import operator

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Multiselect, Button, Group, \
    ManagedMultiselect
from aiogram_dialog.widgets.text import Const, Format

from aiogram.fsm.state import State, StatesGroup

import googlesheets
from handlers import delete_message_after_delay
from settings import PATH_LIST_NAME_FOR_REPORT
from utilites import write_list_of_items_in_file, get_list_items_in_file


class ReportConfigDialog(StatesGroup):
    select_names = State()


async def get_names_data(dialog_manager: DialogManager, **kwargs):
    """
    Загружает список имен для отчета.
    """
    list_of_all_names_for_report = (
        await googlesheets.get_list_of_all_names_from_sheet()
    )
    names = [(name, i) for i, name in enumerate(list_of_all_names_for_report)]
    return {
        "names": names,
    }


async def set_checked_names(start_data: dict, manager: DialogManager):
    """
    Загружает сохраненные выбранные имена и устанавливает их в MultiSelect.
    """
    selected_ids = get_list_items_in_file(PATH_LIST_NAME_FOR_REPORT)
    multiselect: ManagedMultiselect = manager.find("names_multiselect")
    for i in selected_ids:
        await multiselect.set_checked(int(i) , True)


async def on_done_clicked(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    """
    Вызывается при нажатии кнопки "Готово".
    Сохраняет выбранные элементы и завершает диалог.
    """
    selected_ids = manager.find("names_multiselect").get_checked()

    await callback.answer("Сохраняю выбор...")

    write_list_of_items_in_file(selected_ids, PATH_LIST_NAME_FOR_REPORT)

    await callback.message.edit_text(
        f"Отлично! Настройки отчета сохранены. Выбрано {len(selected_ids)} чел.")
    args = manager.start_data.get('command_args')
    if args == 'del':
        context_for_job = {
            "chat_id": callback.message.chat.id,
            "message_id": callback.message.message_id
        }
        asyncio.create_task(
            delete_message_after_delay(callback.bot, context_for_job)
        )

    await manager.done()

report_config_dialog = Dialog(
    Window(
        Const("Выберите сотрудников для включения в отчет по остаткам:"),
        Group(
            Multiselect(
                Format("✓ {item[0]}"),  # Текст для выбранного элемента
                Format("{item[0]}"),  # Текст для невыбранного элемента
                id="names_multiselect",  # Уникальный ID для виджета
                item_id_getter=operator.itemgetter(1),
                # Функция для получения ID из элемента списка
                items="names",  # Ключ из геттера, по которому лежат данные
            ),
            Button(Const("Готово"), id="done_btn",
                   on_click=on_done_clicked),
            width=1
        ),
        state=ReportConfigDialog.select_names,
        getter=get_names_data,
    ),
    on_start=set_checked_names
)


async def configure_report_of_balances(message: Message,
                                       dialog_manager: DialogManager):
    """
    Запускает диалог настройки отчета.
    """
    command = dialog_manager.middleware_data.get('command')
    await dialog_manager.start(ReportConfigDialog.select_names,
                               data={'command_args': command.args},
                               mode=StartMode.RESET_STACK,
                               show_mode=ShowMode.DELETE_AND_SEND)
