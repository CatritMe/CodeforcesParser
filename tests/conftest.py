import asyncio

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from tests.mocked_bot import MockedBot


@pytest_asyncio.fixture(scope='session')
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


# @pytest.fixture()
# def event_loop():
#     return asyncio.get_event_loop()
