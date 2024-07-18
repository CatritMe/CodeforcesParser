from aiogram import types
from unittest.mock import AsyncMock
from aiogram.fsm.context import FSMContext
import pytest
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import User, Chat

from tests.conftest import storage, bot
from tg_bot.keyboard import search_method, tags_builder
from tg_bot.state import SearchProblem
from tg_bot.utils import cmd_start, get_method, get_problem_number, get_tag, get_rating

TEST_USER = User(id=1, is_bot=False, first_name='Test')
TEST_USER_CHAT = Chat(id=1, type='private')


@pytest.mark.asyncio
async def test_cmd_start(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await cmd_start(message, state)
    assert await state.get_state() == SearchProblem.search_method

    message.answer.assert_called_with("Привет, я - бот по поиску задач с сайта Codeforces.com. "
                                      "Ты можешь найти задачи по номеру (если у тебя есть) "
                                      "или по рейтингу и теме задачи\nВыбери нужное", reply_markup=search_method)


@pytest.mark.asyncio
async def test_get_method_search_number(storage, bot):
    message = AsyncMock(text='поиск по номеру')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_method(message, state)
    message.reply.assert_called_with("Отлично, теперь введи номер задачи (например 1925A, 200B (буква английская))",
                                     reply_markup=types.ReplyKeyboardRemove())
    assert await state.get_state() == SearchProblem.put_number


@pytest.mark.asyncio
async def test_get_method_search_rating_and_tag(storage, bot):
    message = AsyncMock(text='поиск по теме и рейтингу')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_method(message, state)
    message.reply.assert_called_with("Выберите тему:", reply_markup=tags_builder.as_markup(resize_keyboard=True),)
    assert await state.get_state() == SearchProblem.put_tag


@pytest.mark.asyncio
async def test_get_method_error(storage, bot):
    message = AsyncMock(text='любое другое сообщение')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_method(message, state)
    message.reply.assert_called_with("Нажми кнопку внизу экрана")


@pytest.mark.asyncio
async def test_get_problem_number_not_isdigit(storage, bot):
    message = AsyncMock(text='любое другое сообщение')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_problem_number(message, state)
    message.reply.assert_called_with('Неправильно введен номер. Первая должна быть цифра')


@pytest.mark.asyncio
async def test_get_problem_number_isdigit_not_search(storage, bot):
    message = AsyncMock(text='5000A')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_problem_number(message, state)
    message.reply.assert_called_with(f'Такой задачи нет.\nПроверь номер, буква должна быть английская',
                                     reply_markup=search_method)
    regdata = await state.get_data()
    assert regdata.get('num') == '5000A'


@pytest.mark.asyncio
async def test_get_problem_number_next_search_num(storage, bot):
    message = AsyncMock(text='Поиск по номеру')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_problem_number(message, state)
    message.reply.assert_called_with(f"Введи номер задачи")
    assert await state.get_state() == SearchProblem.put_number


@pytest.mark.asyncio
async def test_get_problem_number_next_search_tag(storage, bot):
    message = AsyncMock(text='Поиск по теме и рейтингу')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_problem_number(message, state)
    message.reply.assert_called_with("Выберите тему:", reply_markup=tags_builder.as_markup(resize_keyboard=True),)
    assert await state.get_state() == SearchProblem.put_tag


@pytest.mark.asyncio
async def test_get_tag(storage, bot):
    message = AsyncMock(text='math')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_tag(message, state)
    message.reply.assert_called_with(f"Отлично, теперь введи рейтинг (от 800 до 3500 кратно 100)",
                                     reply_markup=types.ReplyKeyboardRemove())
    assert await state.get_state() == SearchProblem.put_rating


@pytest.mark.asyncio
async def test_get_rating_not_isdigit(storage, bot):
    message = AsyncMock(text='высокий')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_rating(message, state)
    message.reply.assert_called_with(f"Рейтинг введен некорректно\nНужно ввести число")


@pytest.mark.asyncio
async def test_get_rating_isdigit_error_rating(storage, bot):
    message = AsyncMock(text='5000')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_rating(message, state)
    message.reply.assert_called_with(f"Рейтинг введен некорректно\n"
                                     f"Укажи рейтинг правильно: от 800 до 3500 кратно 100")


@pytest.mark.asyncio
async def test_get_rating_next_search_num(storage, bot):
    message = AsyncMock(text='Поиск по номеру')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_rating(message, state)
    message.reply.assert_called_with(f"Введи номер задачи")
    assert await state.get_state() == SearchProblem.put_number


@pytest.mark.asyncio
async def test_get_rating_next_search_tag(storage, bot):
    message = AsyncMock(text='Поиск по теме и рейтингу')
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await get_rating(message, state)
    message.reply.assert_called_with("Выберите тему:", reply_markup=tags_builder.as_markup(resize_keyboard=True),)
    assert await state.get_state() == SearchProblem.put_tag
