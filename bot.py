from datetime import time
from pytz import timezone

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler
)

from settings import API_TOKEN
from handlers import (
    notify_assignees_evening,
    notify_assignees_morning,
    report_of_balances,
    report_of_warehouse,
    configure_report_of_balances,
    generate_list_of_names,
    end_configure_report_of_balances,
    help_command,
    good_day,
    nice_rest
)
from utilites import echo


def bot():
    updater = Updater(API_TOKEN)
    dp = updater.dispatcher
    jq = updater.job_queue

    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('report_of_balances', report_of_balances))
    dp.add_handler(CommandHandler('report_of_warehouse', report_of_warehouse))

    configure_report_of_balances_handler = ConversationHandler(
        entry_points=[CommandHandler('config_rep_of_bal', configure_report_of_balances)],
        states={
            1: [
                CallbackQueryHandler(end_configure_report_of_balances, pattern='^Закрыть$'),
                CallbackQueryHandler(generate_list_of_names),
            ],
        },
        fallbacks=[CommandHandler('help', help_command)],
    )
    dp.add_handler(configure_report_of_balances_handler)

    jq.run_daily(notify_assignees_morning, time(9, 00, 00, tzinfo=timezone('Europe/Moscow')))
    jq.run_daily(notify_assignees_evening, time(18, 00, 00, tzinfo=timezone('Europe/Moscow')))
    jq.run_daily(good_day, time(9, 00, 00, tzinfo=timezone('Europe/Moscow')))
    jq.run_daily(nice_rest, time(18, 00, 00, tzinfo=timezone('Europe/Moscow')))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    bot()
