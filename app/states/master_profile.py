from aiogram.fsm.state import State, StatesGroup

class MasterProfileStates(StatesGroup):
    choosing_social_net = State() # Вибір, яку соцмережу додати/змінити
    entering_social_link = State() # Введення самого нікнейму/посилання
    editing_description = State() # Редагування опису
    proposing_service = State() # Пропозиція нової послуги
    choosing_service_category = State() # Вибір категорії для нової послуги
    entering_service_price = State() # Введення ціни для кожної обраної послуги
    proposing_time = State() # Майстер пропонує новий час для запису
