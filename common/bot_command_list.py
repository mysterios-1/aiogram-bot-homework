from aiogram.types import BotCommand


private = [
    BotCommand(command='add_schedule', description='Добавить расписание'),
    BotCommand(command='change_schedule', description='Изменить расписание'),
    BotCommand(command='show_schedule', description='Показать расписание'),
    BotCommand(command='add_hw', description='Добавить д/з'),
    BotCommand(command='change_hw', description='Изменить д/з'),
    BotCommand(command='about', description='О нас'),
]