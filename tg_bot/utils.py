import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from db.database import select_problem_for_id, select_problems_for_rating_tag
from tg_bot.keyboard import search_method, tags_builder
from tg_bot.state import SearchProblem
from services import get_contest_id_index, get_message_format

min_rating = 800
max_rating = 3500
step = 100

load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.getenv('TOKEN'))
# Диспетчер
dp = Dispatcher()


async def cmd_start(message: types.Message, state: FSMContext):
    """Действия по команде старт"""
    await message.answer("Привет, я - бот по поиску задач с сайта Codeforces.com. "
                         "Ты можешь найти задачи по номеру (если у тебя есть) "
                         "или по рейтингу и теме задачи\nВыбери нужное", reply_markup=search_method)
    await state.set_state(SearchProblem.search_method)


async def get_method(message: types.Message, state: FSMContext):
    """
    Выбирает метод поиска задачи:
    - по номеру задачи;
    - по тэгу + рейтингу
    """
    if message.text.lower() == 'поиск по номеру':
        await message.reply("Отлично, теперь введи номер задачи (например 1925A, 200B (буква английская))",
                            reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(SearchProblem.put_number)
    elif message.text.lower() == 'поиск по теме и рейтингу':
        await message.reply(
            "Выберите тему:",
            reply_markup=tags_builder.as_markup(resize_keyboard=True),
        )
        await state.set_state(SearchProblem.get_tag)
    else:
        await message.reply("Нажми кнопку внизу экрана")


async def get_problem_number(message: types.Message, state: FSMContext):
    """
    Запускается, если выбран метод поиска по номеру.
    Возвращает найденную задачу или сообщение об отсутствии
    """
    if message.text[0].isdigit():
        await state.update_data(num=message.text)
        regdata = await state.get_data()
        num = regdata.get('num')
        contest_id, index = get_contest_id_index(num)
        result = await select_problem_for_id(contest_id, index)
        if len(result) == 1:
            problem = get_message_format(result)
            await message.reply(f'Нашел такую задачу:\n\n{problem[0]}', reply_markup=search_method)
        else:
            await message.reply(f'Такой задачи нет.\nПроверь номер, буква должна быть английская',
                                reply_markup=search_method)
    elif message.text == 'Поиск по номеру':
        await state.set_state(SearchProblem.put_number)
        await message.reply(f"Введи номер задачи")
    elif message.text == 'Поиск по теме и рейтингу':
        await state.set_state(SearchProblem.get_tag)
        await message.reply("Выберите тему:", reply_markup=tags_builder.as_markup(resize_keyboard=True),)
    else:
        await message.reply(f'Неправильно введен номер. Первая должна быть цифра')


async def get_tag(message: types.Message, state: FSMContext):
    """
    Запускается, если выбран метод поиска по тэгу + рейтингу.
    Сохраняет введенный тэг
    """
    await state.update_data(tag=message.text)
    await message.reply(f"Отлично, теперь введи рейтинг (от {min_rating} до {max_rating} кратно {step})",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SearchProblem.put_rating)


async def get_rating(message: types.Message, state: FSMContext):
    """
    Запускается, если выбран метод поиска по тэгу + рейтингу.
    Сохраняет введенный рейтинг
    Возвращает найденные задачи из БД
    """
    if message.text.isdigit():
        rating = int(message.text)
        regdata = await state.get_data()
        tag = regdata.get('tag')
        if min_rating <= rating <= max_rating and rating % step == 0:
            await state.update_data(rating=message.text)
            result = await select_problems_for_rating_tag(rating, tag)
            if len(result) > 0:
                problems = get_message_format(result)
                await message.reply(f'Нашел {len(problems)} задач:\n\n{''.join(p for p in problems)}',
                                    reply_markup=search_method)
            else:
                await message.reply(f'Не нашел задачи с таким тэгом + рейтингом\n'
                                    f'Попробуй изменить рейтинг или выбери другой способ поиска',
                                    reply_markup=search_method)
        else:
            await message.reply(f"Рейтинг введен некорректно\n"
                                f"Укажи рейтинг правильно: от {min_rating} до {max_rating} кратно 100")
    elif message.text == 'Поиск по номеру':
        await state.set_state(SearchProblem.put_number)
        await message.reply(f"Введи номер задачи")
    elif message.text == 'Поиск по теме и рейтингу':
        await state.set_state(SearchProblem.get_tag)
        await message.reply("Выберите тему:", reply_markup=tags_builder.as_markup(resize_keyboard=True),)
    else:
        await message.reply(f"Рейтинг введен некорректно\nНужно ввести число")
