from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_category_choice = State()
    waiting_for_new_category_confirmation = State()
    waiting_for_reenter = State()
