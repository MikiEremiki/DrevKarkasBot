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
)


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
    dp.add_handler(CommandHandler('report_of_balances',
                                  report_of_balances))
    dp.add_handler(CommandHandler('report_of_warehouse',
                                  report_of_warehouse))

    configure_report_of_balances_handler = ConversationHandler(
        entry_points=[CommandHandler('config_rep_of_bal',
                                     configure_report_of_balances)],
        states={
            1: [
                CallbackQueryHandler(end_configure_report_of_balances,
                                     pattern='^Закрыть$'),
                CallbackQueryHandler(generate_list_of_names),
            ],
        },
        fallbacks=[CommandHandler('help', help_command)],
    )
    dp.add_handler(configure_report_of_balances_handler)

    dp.add_handler(CommandHandler('rotw', report_of_time_work))
    dp.add_handler(CommandHandler('set_my_name', set_my_name))
    dp.add_handler(CommandHandler('set_start_work', set_start_work))
    dp.add_handler(CommandHandler('set_end_work', set_end_work))
    dp.add_handler(CommandHandler('reset_time_work', reset_time_work))
    dp.add_handler(CallbackQueryHandler(write_choice,
                                        pattern='^Приход$|^Уход$'))

    # Start the Bot
    updater.start_polling()

    dp.run_polling()


if __name__ == '__main__':
    bot()
