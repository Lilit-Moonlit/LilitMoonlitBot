# 🤖 Antigravity Beauty Bot — Документація проекту

> Telegram-бот для запису до майстрів краси. SQLite + Aiogram 3 + APScheduler.

---

## 📁 Структура проекту

```
antigravity/
├── app/
│   ├── main.py              # Точка входу бота
│   ├── config.py            # Налаштування (токен, БД)
│   ├── database/
│   │   ├── models.py        # SQLAlchemy моделі (User, Master, Booking...)
│   │   └── dal.py           # Data Access Layer — всі функції роботи з БД
│   ├── handlers/
│   │   ├── client.py        # Хендлери для клієнтів
│   │   ├── master.py        # Хендлери для майстрів
│   │   └── admin.py         # Хендлери для адміністратора
│   ├── keyboards/           # Inline та Reply клавіатури
│   ├── states/              # FSM стани (реєстрація, бронювання...)
│   └── utils/
│       └── scheduler.py     # APScheduler (нагадування, відгуки)
├── alembic/                 # Міграції бази даних
├── tests/                   # Тести (pytest)
├── scratch/                 # Одноразові скрипти для дебагу
├── docs/                    # ← Ця папка з документацією
├── .env                     # Секретні змінні (не комітити!)
├── beauty_bot.db            # SQLite база даних
├── bot.log                  # Логи бота
├── manage.sh                # Скрипт управління ботом (Linux/WSL)
└── requirements.txt         # Залежності Python
```

---

## ⚙️ Файл `.env`

```env
BOT_TOKEN=ваш_токен_від_BotFather
DATABASE_URL=sqlite+aiosqlite:///beauty_bot.db
```

> ⚠️ Файл `.env` ніколи не комітити в Git!

---

Продовження: [WSL Setup Guide](./wsl_setup.md) | [Команди](./commands.md) | [Нюанси](./gotchas.md)
