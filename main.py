import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from dotenv import load_dotenv

from db.database import update_table
from services import get_problems, get_statistics
from tg_bot.state import SearchProblem
from tg_bot.utils import cmd_start, get_problem_number, get_method, get_tag, get_rating

load_dotenv()

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
    problems_list = get_problems()
    statistics_list = get_statistics()
    task_one = asyncio.create_task(dp.start_polling(bot))
    task_two = asyncio.create_task(update_table(problems_list, statistics_list))
    await asyncio.gather(task_one, task_two)

if __name__ == "__main__":
    asyncio.run(main())
