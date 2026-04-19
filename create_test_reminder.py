import asyncio
import sqlite3
from datetime import datetime, timedelta

def create_test():
    conn = sqlite3.connect('beauty_bot.db')
    cursor = conn.cursor()
    
    # 1. Знаходимо користувача для тесту (беремо першого доступного, або ви можете підставити свій ID)
    cursor.execute("SELECT telegram_id FROM users LIMIT 1")
    user = cursor.fetchone()
    if not user:
        print("Користувачів не знайдено. Спочатку запустіть бота і натисніть /start.")
        return
    
    user_id = user[0]
    
    # 2. Знаходимо будь-якого майстра та його послугу
    cursor.execute("SELECT master_id, id FROM master_services LIMIT 1")
    res = cursor.fetchone()
    if not res:
        print("Майстрів або послуг не знайдено.")
        return
    
    master_id, ms_id = res
    
    # 3. Вираховуємо час: зараз + 60 хвилин
    # Нагадування спрацьовує коли до візиту ЗАЛИШИЛОСЯ рівно 1 година (з похибкою в хвилину)
    start_time = datetime.now() + timedelta(hours=1)
    
    # 4. Створюємо запис зі статусом CONFIRMED
    cursor.execute("""
        INSERT INTO bookings (client_id, master_id, master_service_id, start_time, end_time, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, master_id, ms_id, start_time.strftime("%Y-%m-%d %H:%M:%S"), start_time.strftime("%Y-%m-%d %H:%M:%S"), 'confirmed', datetime.now()))
    
    conn.commit()
    conn.close()
    
    print(f"Test booking created for ID {user_id} at {start_time.strftime('%H:%M')}.")
    print("If the bot is running, you will receive a reminder in about 1 minute.")

if __name__ == "__main__":
    create_test()
