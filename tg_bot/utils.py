import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from db.database import select_problem_for_id
from tg_bot.keyboard import search_method, tags_builder
from tg_bot.state import SearchProblem
from utils import get_contest_id_index

min_rating = 0
max_rating = 3500

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
    if message.text.lower() == 'поиск по номеру':
        await message.reply("Отлично, теперь введи номер задачи (например 1925А, 200B (буква английская))",
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
    await state.update_data(num=message.text)
    regdata = await state.get_data()
    num = regdata.get('num')
    contest_id, index = get_contest_id_index(num)
    result = select_problem_for_id(contest_id, index)
    await bot.send_message(message.from_user.id, f'{result}')


async def get_tag(message: types.Message, state: FSMContext):
    await state.update_data(tag=message.text)
    regdata = await state.get_data()
    tag = regdata.get('tag')
    await message.reply(f"Отлично, теперь введи рейтинг (от {min_rating} до {max_rating} кратно 100)",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SearchProblem.put_rating)


async def get_rating(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        num = int(message.text)
        if min_rating <= num <= max_rating and num % 100 == 0:
            await state.update_data(num=message.text)
            rating = num
            print(rating)
        else:
            await message.reply(f"Рейтинг введен некорректно\n"
                                f"Укажи рейтинг правильно: от {min_rating} до {max_rating} кратно 100")
    else:
        await message.reply(f"Рейтинг введен некорректно\n"
                            f"Нужно ввести число")
