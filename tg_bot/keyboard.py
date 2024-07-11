from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

tags = ['dfs and similar', 'divide and conquer', 'graphs', 'combinatorics', 'dp',
'math', 'brute force', 'data structures',
'greedy', 'sortings', 'two pointers', 'strings', 'implementation',
'interactive', '797', 'dsu', 'games', 'hashing',
'number theory', 'binary search', 'geometry', 'constructive algorithms',
'string suffix structures', 'bitmasks',
'probabilities', 'meet-in-the-middle', 'matrices', 'ternary search', 'fft',
'shortest paths', '2-sat', 'flows',
'*special', 'graph matchings', 'schedules', 'expression parsing', 'chinese remainder theorem']

search_method = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Поиск по номеру"),
                types.KeyboardButton(text="Поиск по теме и рейтингу")
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите способ поиска"
    )

tags_builder = ReplyKeyboardBuilder()
for tag in tags:
    tags_builder.add(types.KeyboardButton(text=str(tag)))
tags_builder.adjust(6)

