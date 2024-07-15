from aiogram import types
from unittest.mock import AsyncMock
from aiogram.fsm.context import FSMContext
import pytest
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import User, Chat

from tests.conftest import storage, bot
from tg_bot.keyboard import search_method, tags_builder
from tg_bot.state import SearchProblem
from tg_bot.utils import cmd_start, get_method, get_problem_number

TEST_USER = User(id=1, is_bot=False, first_name='Test')
TEST_USER_CHAT = Chat(id=1,type='private')


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
    assert await state.get_state() == SearchProblem.get_tag


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



# pytest tests/test_bot.py