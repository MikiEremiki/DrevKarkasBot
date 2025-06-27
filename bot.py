import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeChat,
    BotCommandScopeAllPrivateChats
)
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from log.logging_config import load_log_config
from settings import API_TOKEN
from utilites import echo
from handlers import (
    start,
    notify_assignees_evening,
    notify_assignees_morning,
    report_of_balances,
    report_of_warehouse,
    configure_report_of_balances,
    generate_list_of_names,
    end_configure_report_of_balances,
    help_command,
    good_day,
    nice_rest,
    report_of_time_work,
    write_choice,
    set_my_name,
    set_start_work,
    set_end_work,
    reset_time_work,
    ConfigReportStates,
)
from googlesheets import agcm


async def main():
    bot_logger = load_log_config()
    bot_logger.info('Инициализация бота')

    bot = Bot(token=API_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_my_commands(BotCommandScopeDefault())
    await bot.delete_my_commands(BotCommandScopeAllPrivateChats())
    await bot.delete_my_commands(BotCommandScopeChat(chat_id=454342281))
    await bot.delete_my_commands(BotCommandScopeChat(chat_id=5477576195))
    await bot.set_my_commands([
        BotCommand(command='start', description='Старт/Перезапуск бота'),
    ],
        scope=BotCommandScopeDefault()
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, agcm=agcm)

    scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))

    dp.message.register(start, Command(commands=['start']))
    dp.message.register(echo, Command(commands=['echo']))
    dp.message.register(help_command, Command(commands=['help']))
    dp.message.register(report_of_balances,
                        Command(commands=['report_of_balances']))
    dp.message.register(report_of_warehouse,
                        Command(commands=['report_of_warehouse']))

    dp.message.register(configure_report_of_balances,
                        Command(commands=['config_rep_of_bal']))
    dp.callback_query.register(end_configure_report_of_balances,
                               F.data == 'Закрыть',
                               ConfigReportStates.waiting_for_selection)
    dp.callback_query.register(generate_list_of_names,
                               ConfigReportStates.waiting_for_selection)

    dp.message.register(report_of_time_work, Command(commands=['rotw']))
    dp.message.register(set_my_name, Command(commands=['set_my_name']))
    dp.message.register(set_start_work, Command(commands=['set_start_work']))
    dp.message.register(set_end_work, Command(commands=['set_end_work']))
    dp.message.register(reset_time_work, Command(commands=['reset_time_work']))

    dp.callback_query.register(write_choice, F.data.in_(['Приход', 'Уход']))

    scheduler.add_job(
        notify_assignees_morning, 'cron', args=[bot], hour=9, minute=0)
    scheduler.add_job(
        notify_assignees_evening, 'cron', args=[bot], hour=18, minute=0)
    scheduler.add_job(
        good_day, 'cron', args=[bot], day_of_week=0, hour=9, minute=0)
    scheduler.add_job(
        nice_rest, 'cron', args=[bot], day_of_week=4, hour=18, minute=0)

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
