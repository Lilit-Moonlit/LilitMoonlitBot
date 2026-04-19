from aiogram.fsm.state import State, StatesGroup

class ReviewStates(StatesGroup):
    # Клієнт про майстра
    client_rating = State()
    client_comment = State()
    
    # Майстер про клієнта
    master_rating = State()
    master_comment = State()
