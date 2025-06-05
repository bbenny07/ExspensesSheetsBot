from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_category_choice = State()
    waiting_for_new_category_confirmation = State()
    waiting_for_reenter = State()
    waiting_for_feedback = State()

class ViewTable(StatesGroup):
    viewing_row = State()
    
class EditRowState(StatesGroup):
    waiting_for_edit_row = State()
    waiting_for_edit_category_confirmation = State()
    waiting_for_edit_category_choice = State()