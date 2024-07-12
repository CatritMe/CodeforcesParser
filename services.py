import time

import requests
import schedule

contest = requests.get('https://codeforces.com/api/problemset.problems?}')


def get_problems():
    """
    Получает и возвращает список задач с сайта codeforces
    """
    problems = []
    result = contest.json()['result']['problems']
    for i in range(0, len(result)):
        problems.append(result[i])
    return problems


def get_statistics():
    """
    Получает и возвращает статистику с сайта codeforces
    """
    statistics = []
    statistic = contest.json()['result']['problemStatistics']
    for i in range(0, len(statistic)):
        statistics.append(statistic[i])
    return statistics


def get_tags():
    """
    Получает и возвращает список тэгов
    """
    tags = []
    result = contest.json()['result']['problems']
    for res in result:
        for tag in res['tags']:
            if tag not in tags:
                tags.append(tag)
    return tags


def get_contest_id_index(num):
    """
    Получает contest_id: int и index: str из строки
    """
    contest_id = int(''.join(num[i] if num[i].isdigit() and i <= 4 else '' for i in range(len(num))))
    index = ''.join(num[i].upper() if not num[i].isdigit() or i > 4 else '' for i in range(len(num)))
    index.upper()
    return contest_id, index


def get_message_format(result):
    """
    Форматирует список задач для отправки в сообщении, возвращает список строк
    """
    problems = []
    for r in result:
        problem = (f'Номер задачи: {r.contest_id}{r.index}\n'
                   f'Название: {r.name}\n'
                   f'Рейтинг: {r.rating}\n'
                   f'Количество решивших задачу: {r.solved_count}\n'
                   f'Тэги: {', '.join(tag.tag_name for tag in r.tags)}\n'
                   f'-----------------------------------\n')
        problems.append(problem)
    return problems


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
