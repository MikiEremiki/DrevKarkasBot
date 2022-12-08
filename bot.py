from datetime import time
from pytz import timezone

from telegram.ext import Updater, CommandHandler

from settings import API_TOKEN
from handlers import notify_assignees_evening, notify_assignees_morning, report_of_balances, report_of_warehouse
from utilites import echo


def bot():
    updater = Updater(API_TOKEN)
    dp = updater.dispatcher
    jq = updater.job_queue

    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(CommandHandler('Отчет по балансу', report_of_balances))
    dp.add_handler(CommandHandler('Отчет по складу', report_of_warehouse))

    jq.run_daily(notify_assignees_morning, time(9, 00, 00, tzinfo=timezone('Europe/Moscow')))
    jq.run_daily(notify_assignees_evening, time(18, 00, 00, tzinfo=timezone('Europe/Moscow')))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    bot()
