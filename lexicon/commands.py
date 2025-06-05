from lexicon import messages, categories

COMMANDS_INFO: dict[str, str] = {
    '/start': 'Запустить бота и создать личную таблицу',
    '/help': 'Показать справку по использованию бота',
    '/categories': 'Показать список всех доступных категорий',
    '/feedback': 'Написать разработчику',
    '/table': 'Посмотреть и редактировать таблицу'
}

COMMANDS_RESPONSES: dict[str, str] = {
    '/start': messages.START,
    '/help': messages.HELP,
    '/categories': categories.CATEGORIES_LIST,
    '/feedback': messages.FEEDBACK,
    '/table': messages.TABLE
}
