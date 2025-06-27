import os

from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest


async def delete_message(bot: Bot, chat_id, path):
    list_message_id_for_delete = get_list_items_in_file(path)
    if len(list_message_id_for_delete) == 2:
        try:
            await bot.delete_message(
                chat_id=chat_id,
                message_id=int(list_message_id_for_delete[0])
            )
        except TelegramBadRequest:
            print('Сообщение уже удалено')
        list_message_id_for_delete.pop(0)
        write_list_of_items_in_file(list_message_id_for_delete, path)


def save_message_for_delete(message_id, path):
    list_message_id_for_delete = get_list_items_in_file(path)
    list_message_id_for_delete.append(message_id)
    write_list_of_items_in_file(list_message_id_for_delete, path)


async def echo(message: Message):
    text = ('chat_id = <code>' +
            str(message.chat.id) + '</code>\n' +
            'user_id = <code>' +
            str(message.from_user.id) + '</code>\n' +
            'is_forum = <code>' +
            str(message.chat.is_forum) + '</code>\n' +
            'message_thread_id = <code>' +
            str(message.message_thread_id) + '</code>')
    await message.answer(text)


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


async def delete_message_for_job_in_callback(bot: Bot, data: dict):
    await bot.delete_message(
        chat_id=data['chat_id'],
        message_id=data['message_id']
    )


def check_path(path):
    current_path = os.getcwd()
    path = os.path.join(current_path, path)
    if not os.path.exists(path):
        os.makedirs(path)
