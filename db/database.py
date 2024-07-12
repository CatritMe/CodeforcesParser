import asyncio
import datetime
import logging
import os
import random
import time

import schedule
from dotenv import load_dotenv

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, URL, delete, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker, selectinload, aliased
from db.meta import metadata, Tag, Problem
from services import get_problems, get_statistics, get_tags, get_contest_id_index

load_dotenv()

username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database_name = os.getenv('DB_NAME')
db_url = URL.create('postgresql+psycopg2',
                    username=username,
                    password=password,
                    host=host,
                    port=port,
                    database=database_name
                    )
async_db_url = URL.create('postgresql+asyncpg',
                    username=username,
                    password=password,
                    host=host,
                    port=port,
                    database=database_name
                    )

engine = create_engine(db_url, echo=True)
async_engine = create_async_engine(async_db_url, echo=True)
session = sessionmaker(engine)
async_session = async_sessionmaker(async_engine)


def create_db(db_name):
    """
    Создание БД
    """
    connection = psycopg2.connect(user=username, password=password)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(f'drop database {db_name}')
    cursor.execute(f'create database {db_name}')
    cursor.close()
    connection.close()


def create_table() -> Session:
    """
    Создание таблиц
    """
    metadata.drop_all(bind=engine)
    metadata.create_all(bind=engine)
    return Session(bind=engine)


def insert_data(problems, statistics, tags):
    """
    Вставка спарсенных данных в БД
    Ничего не возвращает
    """
    with session() as s:
        for tag in tags:
            tg = Tag(tag_name=tag)
            s.add(tg)
        for problem in problems:

            for i in range(len(statistics)):
                if statistics[i]['contestId'] == problem['contestId'] and statistics[i]['index'] == problem['index']:
                    solved_count = statistics[i]['solvedCount']

            try:
                rating = problem['rating']
            except KeyError:
                rating = 0

            prob = Problem(
                contest_id=problem['contestId'],
                index=problem['index'],
                name=problem['name'],
                rating=rating,
                solved_count=solved_count
            )
            if problem['tags']:
                for tag in problem['tags']:
                    tg = s.get(Tag, tag)
                    if tg not in prob.tags:
                        prob.tags.append(tg)

            s.add(prob)
        s.commit()


async def update_table(problems, statistics):
    """
    Функция для шедулера
    Обновляет БД, если на сайте codeforces есть изменения
    Не возвращает ничего, но в консоль пишет, если есть изменения и время парсинга
    """
    async with async_session() as s:
        engine.echo = False
        for problem in problems[0:100]:
            query = (
                select(Problem)
                .options(selectinload(Problem.tags))
                .filter_by(contest_id=problem['contestId'], index=problem['index'])
            )
            res = await s.execute(query)
            result = res.unique().scalars().all()

            for i in range(len(statistics)):
                if statistics[i]['contestId'] == problem['contestId'] and statistics[i]['index'] == problem['index']:
                    solved_count = statistics[i]['solvedCount']
            if len(result) == 0:
                try:
                    rating = problem['rating']
                except KeyError:
                    rating = 0

                prob = Problem(
                    contest_id=problem['contestId'],
                    index=problem['index'],
                    name=problem['name'],
                    rating=rating,
                    solved_count=solved_count
                )
                if problem['tags']:
                    for tag in problem['tags']:
                        tg = s.get(Tag, tag)
                        if tg not in prob.tags:
                            prob.tags.append(tg)
                s.add(prob)
                print('добавлена новая')
            elif int(solved_count) > int(result[0].solved_count):
                result[0].solved_count = solved_count
        await s.commit()
        engine.echo = True
        print(f'парсинг в {datetime.datetime.now()}')


async def select_problem_for_id(contest_id, index):
    """
    Возвращает задачу из БД, найденную по указанным данным или пустой список
    """
    async with async_session() as s:
        query = (
            select(Problem)
            .options(selectinload(Problem.tags))
            .filter_by(contest_id=contest_id, index=index)
        )
        res = await s.execute(query)
        result = res.unique().scalars().all()
        return result


async def select_problems_for_rating_tag(rating, tag):
    """
    Возвращает 10 задач из списка по принципу:
    1. по указанной тематике меньше 10 задач в базе (возвращает все найденные)
    2. возвращает 10 рандомных задач с одним указанным тэгом
    3. возвращает 10 рандомных задач с двумя тэгами, включая указанный
    4. возвращает 10 рандомных задач с более чем тремя тэгами, включая указанный
    5. если в каждой категории найдено меньше 10 задач, то возвращает самый длинный список задач
    """
    async with async_session() as s:
        result_1_tag = []
        result_2_tags = []
        result_3_tags = []

        query = (
            select(Problem)
            .join(Problem.tags)
            .options(selectinload(Problem.tags))
            .where(Tag.tag_name == tag).where(Problem.rating == rating)
        )
        res = await s.execute(query)
        result = res.unique().scalars().all()

        if len(result) < 10:
            return result
        else:
            for r in result:
                if len(r.tags) == 1:
                    result_1_tag.append(r)
                elif len(r.tags) == 2:
                    result_2_tags.append(r)
                elif len(r.tags) > 3:
                    result_3_tags.append(r)
            if len(result_1_tag) > 10:
                random.shuffle(result_1_tag)
                return result_1_tag[0:10]
            elif len(result_2_tags) > 10:
                random.shuffle(result_2_tags[0:10])
                return result_2_tags[0:10]
            elif len(result_3_tags) > 10:
                random.shuffle(result_3_tags)
                return result_3_tags[0:10]
            else:
                if len(result_1_tag) > len(result_2_tags) and len(result_1_tag) > len(result_3_tags):
                    return result_1_tag
                elif len(result_2_tags) > len(result_1_tag) and len(result_2_tags) > len(result_3_tags):
                    return result_2_tags
                elif len(result_3_tags) > len(result_1_tag) and len(result_3_tags) > len(result_2_tags):
                    return result_3_tags


def main():
    create_db(database_name)
    create_table()
    insert_data(get_problems(), get_statistics(), get_tags())
    # schedule.every(1).hours.do(update_table, problems_list, statistics_list)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)


if __name__ == "__main__":
    main()
