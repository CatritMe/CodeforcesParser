import requests

contest = requests.get('https://codeforces.com/api/problemset.problems?}')


def get_problems():
    """Получает задачи с сайта codeforces"""
    problems = []
    result = contest.json()['result']['problems']
    for i in range(0, len(result)):
        problems.append(result[i])
    return problems


def get_statistics():
    """Получает статистику с сайта codeforces"""
    statistics = []
    statistic = contest.json()['result']['problemStatistics']
    for i in range(0, len(statistic)):
        statistics.append(statistic[i])
    return statistics


def get_tags():
    """Получает список тэгов"""
    tags = []
    result = contest.json()['result']['problems']
    for res in result:
        for tag in res['tags']:
            if tag not in tags:
                tags.append(tag)
    return tags


def get_contest_id_index(num):
    """получает contest_id: int и index: str из строки"""
    contest_id = int(''.join(num[i] if num[i].isdigit() and i <= 4 else '' for i in range(len(num))))
    index = ''.join(num[i].upper() if not num[i].isdigit() or i > 4 else '' for i in range(len(num)))
    index.upper()
    return contest_id, index