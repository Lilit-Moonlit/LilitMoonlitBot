from aiogram.fsm.state import State, StatesGroup

class ClientBooking(StatesGroup):
    waiting_for_service_selection = State()
    waiting_for_match_type = State()
    waiting_for_date_time = State()
    waiting_for_booking_comment = State()
    waiting_for_master_response = State()
    waiting_for_negotiation = State()
    waiting_for_custom_service_description = State()
