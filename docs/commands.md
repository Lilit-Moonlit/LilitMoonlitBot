# 📋 Всі важливі команди

## 🤖 Управління ботом (WSL/Ubuntu)

| Команда | Що робить |
|---------|-----------|
| `bash manage.sh start` | Запустити бота у фоні |
| `bash manage.sh stop` | Зупинити бота |
| `bash manage.sh restart` | Рестартувати бота |
| `bash manage.sh status` | Перевірити чи запущений + останні логи |
| `bash manage.sh logs` | Слідкувати за логами в реальному часі (Ctrl+C щоб вийти) |

---

## 🐍 Virtual Environment (venv)

```bash
# --- WSL/Ubuntu ---
# Створити venv (один раз)
python3 -m venv venv_linux

# Встановити залежності
./venv_linux/bin/pip install -r requirements.txt

# Запустити бота напряму (без manage.sh)
./venv_linux/bin/python -m app.main

# Запустити будь-який скрипт
./venv_linux/bin/python seed.py
./venv_linux/bin/python update_services.py
./venv_linux/bin/python migrate_cats.py
```

```powershell
# --- Windows PowerShell (для локальної розробки) ---
# Активувати venv
.\venv\Scripts\Activate.ps1

# Якщо помилка ExecutionPolicy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Після активації можна писати просто:
python -m app.main
python seed.py
```

---

## 🗄️ База даних (SQLite)

```bash
# Перевірити що БД файл існує
ls -la beauty_bot.db

# Відкрити SQLite консоль (якщо встановлено)
sqlite3 beauty_bot.db

# Корисні SQLite команди всередині консолі:
.tables              # список таблиць
.schema users        # структура таблиці users
SELECT * FROM users; # всі юзери
SELECT * FROM bookings ORDER BY created_at DESC LIMIT 5;  # останні записи
.quit                # вийти
```

---

## 🔄 Alembic (міграції БД)

```bash
# Перевірити поточну версію міграції
./venv_linux/bin/alembic current

# Застосувати всі нові міграції
./venv_linux/bin/alembic upgrade head

# Відкотити останню міграцію
./venv_linux/bin/alembic downgrade -1

# Переглянути історію міграцій
./venv_linux/bin/alembic history
```

> ⚠️ **Зазвичай alembic НЕ потрібен для SQLite** — таблиці створюються автоматично при першому запуску.

---

## 🧪 Тести (pytest)

```bash
# Запустити всі тести
./venv_linux/bin/pytest

# Запустити конкретний файл
./venv_linux/bin/pytest tests/test_dal.py

# Запустити з виводом
./venv_linux/bin/pytest -v

# Запустити з виводом print() 
./venv_linux/bin/pytest -s -v
```

---

## 📝 Логи

```bash
# Живі логи (слідкувати в реальному часі)
tail -f bot.log

# Останні 50 рядків логів
tail -n 50 bot.log

# Пошук помилок в логах
grep -i "error\|exception\|critical" bot.log

# Очистити лог (коли він занадто великий)
> bot.log
```

---

## 🐛 Дебаг скрипти

```bash
# Перевірити змінні оточення (.env)
./venv_linux/bin/python check_env.py

# Список всіх послуг в БД
./venv_linux/bin/python scratch/list_all_services.py

# Список категорій
./venv_linux/bin/python scratch/list_categories.py

# Засіяти БД тестовими даними
./venv_linux/bin/python seed.py

# Тесту нагадувань
./venv_linux/bin/python create_test_reminder.py
```

---

## 🔍 Перевірка процесів

```bash
# Чи запущений бот?
pgrep -f "python.*-m app.main"

# Всі Python процеси
ps aux | grep python

# Вбити зависший процес бота (замінить PID на реальний)
kill -9 $(pgrep -f "python.*-m app.main")

# Перевірити PID файл
cat bot.pid
```
