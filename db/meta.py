from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey, CHAR, create_engine, URL, delete, \
    ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship, backref, Session, Mapped, mapped_column

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Tag(Base):
    __tablename__ = "tags"
    # tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(primary_key=True)
    problems: Mapped[list['Problem']] = relationship(
        back_populates='tags',
        secondary='problems_tags'
    )


class Problem(Base):
    __tablename__ = "problems"
    contest_id: Mapped[int]
    index: Mapped[str]
    name: Mapped[str]
    rating: Mapped[int]
    solved_count: Mapped[int] = mapped_column(default=None)
    # group: Mapped[int] = mapped_column(default=None)
    tags: Mapped[list['Tag']] = relationship(
        back_populates='problems',
        secondary='problems_tags'
    )
    __table_args__ = (
        PrimaryKeyConstraint('contest_id', 'index', name='problem_pk'),
    )


class ProblemTag(Base):
    __tablename__ = "problems_tags"
    tag_name: Mapped[str] = mapped_column(ForeignKey('tags.tag_name', ondelete='CASCADE'), primary_key=True,)
    contest_id: Mapped[int]
    index: Mapped[str]
    __table_args__ = (
        ForeignKeyConstraint(['contest_id', 'index'], ['problems.contest_id', 'problems.index'],
                             name='problem_tag_pk'),
        PrimaryKeyConstraint('contest_id', 'index', 'tag_name', name='prob_tag_pk'),
    )
