from aiogram.fsm.state import State, StatesGroup

class AdStates(StatesGroup):
    # Пошук моделі
    model_service = State()
    model_datetime = State()
    model_location = State()
    model_requirements = State()
    model_price = State()
    model_contact = State()
    model_photo = State()
    model_video = State()
    model_preview = State()

    # Вакансії
    vacancy_position = State()
    vacancy_company = State()
    vacancy_salary = State()
    vacancy_location = State()
    vacancy_requirements = State()
    vacancy_contact = State()
    vacancy_photo = State()
    vacancy_video = State()
    vacancy_preview = State()

class QuickAdStates(StatesGroup):
    waiting_for_content = State()
    preview = State()
