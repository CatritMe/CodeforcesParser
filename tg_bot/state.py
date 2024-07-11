from aiogram.fsm.state import State, StatesGroup


class SearchProblem(StatesGroup):

    search_method = State()
    put_number = State()
    get_tag = State()
    put_rating = State()
