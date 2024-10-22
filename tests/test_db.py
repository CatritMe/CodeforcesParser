import pytest
from sqlalchemy.exc import IntegrityError

from db.database import engine, session, select_problems_for_rating_tag
from db.meta import Base, Problem, Tag, ProblemTag


class TestDB:
    def setup_class(self):
        Base.metadata.create_all(engine)
        self.session = session()
        self.valid_problem = Problem(
            contest_id=9000,
            index='A',
            rating=1000,
            solved_count=10000,
            name='Test'
        )
        self.valid_tag = Tag(
            tag_name='mathTest'
        )

    def teardown_class(self):
        self.session.rollback()
        self.session.close()

    def test_problem_valid(self):
        self.session.add(self.valid_problem)
        self.session.commit()
        result = self.session.query(Problem).filter_by(contest_id=9000).first()
        assert result.index == "A"
        assert result.name != "Problem1"
        assert result.rating == 1000
        self.session.delete(self.valid_problem)
        self.session.commit()

    @pytest.mark.xfail(raises=IntegrityError)
    def test_problem_no_name(self):
        problem = Problem(
            contest_id=9002,
            index='A',
            rating=1000,
            solved_count=10000
        )
        self.session.add(problem)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def test_problem_tag_valid(self):
        valid_prob = Problem(
            contest_id=9003,
            index='A',
            rating=1000,
            solved_count=10000,
            name='TestCase',
            tags=[self.valid_tag]
        )
        self.session.add(valid_prob)
        self.session.commit()
        sample_tag = self.session.query(ProblemTag).filter_by(tag_name='mathTest').first()
        assert sample_tag.contest_id == 9003
        assert sample_tag.index == 'A'
        assert sample_tag.tag_name != 1
        self.session.delete(valid_prob)
        self.session.delete(self.valid_tag)
        self.session.commit()

    @pytest.mark.asyncio
    @pytest.mark.xfail(raises=AttributeError)
    async def test_select_problems_for_rating_tag(self):
        result = await select_problems_for_rating_tag(3000, 'math')
        try:
            assert len(result) == 10
        except AttributeError:
            print('ошибка event_loop')
        self.session.close()
