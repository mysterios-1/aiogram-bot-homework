from aiogram.types import BotCommand


private = [
    BotCommand(command='about', description='О нас'),
    BotCommand(command='add_schedule', description='Добавить расписание'),
    BotCommand(command='change_schedule', description='Изменить расписание'),
    BotCommand(command='add_hw', description='Добавить д/з'),
    BotCommand(command='change_hw', description='Изменить д/з'),
]