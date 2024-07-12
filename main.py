import asyncio
import logging
import os
import threading

import schedule
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from db.database import update_table
from scheduler import on_startup
from services import run_scheduler, get_problems, get_statistics
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
    problems_list = get_problems()
    statistics_list = get_statistics()
    task_one = asyncio.create_task(dp.start_polling(bot))
    task_two = asyncio.create_task(update_table(problems_list, statistics_list))
    await asyncio.gather(task_one, task_two)

if __name__ == "__main__":
    asyncio.run(main())
