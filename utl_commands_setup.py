from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeChat,
    BotCommandScopeAllPrivateChats
)


async def setup_commands(bot):
    await bot.delete_my_commands(BotCommandScopeDefault())
    await bot.delete_my_commands(BotCommandScopeAllPrivateChats())
    await bot.delete_my_commands(BotCommandScopeChat(chat_id=454342281))
    await bot.delete_my_commands(BotCommandScopeChat(chat_id=5477576195))
    await bot.set_my_commands([
        BotCommand(command='start', description='Старт/Перезапуск бота'),
        BotCommand(command='report_of_balances', description='Отчет по балансам'),
    ],
        scope=BotCommandScopeDefault()
    )
