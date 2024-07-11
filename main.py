import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv

from tg_bot.state import SearchProblem
from tg_bot.utils import cmd_start, get_problem_number, get_method, get_tag, get_rating

load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.getenv('TOKEN'))
# Диспетчер
dp = Dispatcher()

dp.message.register(cmd_start, Command(commands='start'))
dp.message.register(get_method, SearchProblem.search_method)
dp.message.register(get_problem_number, SearchProblem.put_number)
dp.message.register(get_tag, SearchProblem.get_tag)
dp.message.register(get_rating, SearchProblem.put_rating)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())