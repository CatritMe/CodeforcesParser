import datetime
import logging
import os
import time

import schedule
from dotenv import load_dotenv

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, URL, delete, select
from sqlalchemy.orm import Session, sessionmaker, selectinload, aliased
from db.meta import metadata, Tag, Problem
from utils import get_problems, get_statistics, get_tags, get_contest_id_index

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

engine = create_engine(db_url, echo=True)
session = sessionmaker(engine)


def create_db(db_name):
    """Создание БД"""
    connection = psycopg2.connect(user=username, password=password)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(f'drop database {db_name}')
    cursor.execute(f'create database {db_name}')
    cursor.close()
    connection.close()


def create_table() -> Session:
    """Создание таблиц"""
    metadata.drop_all(bind=engine)
    metadata.create_all(bind=engine)
    return Session(bind=engine)


def insert_data(problems, statistics, tags):
    """Вставка спарсенных данных в БД"""
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


def update_table(problems, statistics):
    with session() as s:
        engine.echo = False
        for problem in problems[0:100]:
            query = (
                select(Problem)
                .options(selectinload(Problem.tags))
                .filter_by(contest_id=problem['contestId'], index=problem['index'])
            )
            res = s.execute(query)
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
        s.commit()
        engine.echo = True
        print(f'парсинг в {datetime.datetime.now()}')


def select_problem_for_id(contest_id, index):
    with session() as s:
        query = (
            select(Problem)
            .options(selectinload(Problem.tags))
            .filter_by(contest_id=contest_id, index=index)
        )
        res = s.execute(query)
        try:
            result = res.unique().scalars().all()[0]
            name = result.name
            rat = result.rating
            solved_count = result.rating
            tags = []
            for tag in result.tags:
                tags.append(tag.tag_name)
            print(result)
        except IndexError:
            print('Задача с таким номером не найдена')


def select_problems_for_rating_tag(rating, tag):
    with session() as s:
        query = (
            select(Problem)
            .join(Problem.tags)
            .where(Tag.tag_name == tag).where(Problem.rating == rating)
        )
        res = s.execute(query)
        result = res.unique().scalars().all()
        final_result = []
        for r in result:
            if r.tags[0].tag_name == tag and len(r.tags) == 1:
                final_result.append(r)
        if len(final_result) < 10:
            for r in result:
                if r.tags[0].tag_name == tag and r not in final_result:
                    final_result.append(r)
        if len(final_result) < 10:
            for r in result:
                if len(r.tags) > 1:
                    if r.tags[1].tag_name == tag and len(final_result) < 10:
                        final_result.append(r)
        # for fr in final_result:
        #     tags = []
        #     for tag in fr.tags:
        #         tags.append(tag.tag_name)
        #     print(fr.name, tags)
        for fr in result:
            tags = []
            for tag in fr.tags:
                tags.append(tag.tag_name)
            print(fr.name, tags)


def main():
    # create_db(database_name)
    # create_table()
    problems_list = get_problems()
    statistics_list = get_statistics()
    tags = get_tags()
    # schedule.every(1).hours.do(update_table, problems_list, statistics_list)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    # insert_data(problems_list, statistics_list, tags)
    # update_table(problems_list, statistics_list)
    # contest_id, index = get_contest_id_index('1976B')
    # select_problem_for_id(25455, 'S')
    select_problems_for_rating_tag(3500, 'ternary search')


if __name__ == "__main__":
    main()
