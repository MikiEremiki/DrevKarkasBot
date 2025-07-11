import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from log.logging_config import load_log_config
from report_balance_config_dialog import (
    configure_report_of_balances,
    report_config_dialog
)
from settings import API_TOKEN
from utilites import echo
from handlers import (
    start,
    notify_assignees_evening,
    notify_assignees_morning,
    report_of_balances,
    report_of_warehouse,
    help_command,
    good_day,
    nice_rest,
    report_of_time_work,
    write_choice,
    set_my_name,
    set_start_work,
    set_end_work,
    reset_time_work,
)
from googlesheets import agcm
from utl_commands_setup import setup_commands


async def main():
    bot_logger = load_log_config()
    bot_logger.info('Инициализация бота')

    bot = Bot(token=API_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await setup_commands(bot)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, agcm=agcm)

    scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))

    dp.message.register(start, Command('start'))
    dp.message.register(echo, Command('echo'))
    dp.message.register(help_command, Command('help'))
    dp.message.register(report_of_balances,
                        Command('report_of_balances'))
    dp.message.register(report_of_warehouse,
                        Command('report_of_warehouse'))

    dp.message.register(report_of_time_work, Command('rotw'))
    dp.message.register(set_my_name, Command('set_my_name'))
    dp.message.register(set_start_work, Command('set_start_work'))
    dp.message.register(set_end_work, Command('set_end_work'))
    dp.message.register(reset_time_work, Command('reset_time_work'))

    dp.callback_query.register(write_choice, F.data.in_(['Приход', 'Уход']))

    dp.message.register(configure_report_of_balances, Command("config_rep_of_bal"))
    dp.include_router(report_config_dialog)
    setup_dialogs(dp)

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
