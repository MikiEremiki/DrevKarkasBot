from datetime import time
from pytz import timezone

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    PicklePersistence,
    Defaults
)

from log.logging_config import load_log_config
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
    bot_logger = load_log_config()
    bot_logger.info('Инициализация бота')

    defaults = Defaults(
        tzinfo=timezone('Europe/Moscow')
    )
    persistence = PicklePersistence(filepath="db/conversationbot")
    application = (
        Application.builder()
        .token(API_TOKEN)
        .persistence(persistence)
        .defaults(defaults)

        .build()
    )
    del defaults

    dp = application
    jq = dp.job_queue

    dp.add_handler(CommandHandler('start', start))
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
    jq.run_daily(good_day, time(9, 00, 00, tzinfo=timezone('Europe/Moscow')), days=[0])
    jq.run_daily(nice_rest, time(18, 00, 00, tzinfo=timezone('Europe/Moscow')), days=[4])

    # Start the Bot
    updater.start_polling()

    dp.run_polling()


if __name__ == '__main__':
    bot()
