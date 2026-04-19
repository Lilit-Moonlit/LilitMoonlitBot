from aiogram.fsm.state import State, StatesGroup

class ClientRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

class MasterRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_portfolio = State()

class ServiceAddition(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_duration = State()
