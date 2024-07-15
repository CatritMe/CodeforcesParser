import pytest

from db.database import engine, session
from db.meta import Base, Problem
from services import get_problems, get_statistics, get_tags, get_contest_id_index, get_message_format

Base.metadata.create_all(engine)
session = session()

def test_get_problems_len():
    problems = get_problems()
    assert len(problems[0]) == 6


def test_get_problems_no_key():
    problems = get_problems()
    with pytest.raises(KeyError):
        problem_id = problems[0]['problem_id']


def test_get_statistics():
    stat = get_statistics()
    assert len(stat[0]) == 3


def test_get_tags():
    tags = get_tags()
    assert len(tags) == 37


def test_get_contest_id_index():
    assert get_contest_id_index('125d') == (125, 'D')
    assert get_contest_id_index('2354a1') == (2354, 'A1')


def test_get_message_format():
    result = session.query(Problem).filter_by(contest_id=1, index='A').all()
    prob = get_message_format(result)
    assert prob[0] == (f'Номер задачи: {result[0].contest_id}{result[0].index}\n'
                       f'Название: {result[0].name}\n'
                       f'Рейтинг (сложность): {result[0].rating}\n'
                       f'Количество решивших задачу: {result[0].solved_count}\n'
                       f'Тэги: {', '.join(tag.tag_name for tag in result[0].tags)}\n'
                       f'-----------------------------------\n')
