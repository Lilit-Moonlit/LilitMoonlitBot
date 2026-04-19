# ⚠️ Нюанси та типові проблеми

## 1. venv_linux vs venv — НЕ плутати!

```
venv/         ← Windows (PowerShell). НЕ працює в WSL!
venv_linux/   ← WSL/Ubuntu (bash).    НЕ працює в PowerShell!
```

**Симптом:** `No module named aiogram` або `Bad interpreter` — значить використовуєш не той venv.

**Рішення:**
- У WSL завжди: `./venv_linux/bin/python`
- У PowerShell завжди: `.\venv\Scripts\python.exe`

---

## 2. Шлях до проекту в WSL

Windows шляхи конвертуються так:
```
C:\Users\Surface\Desktop\antigravity
→
/mnt/c/Users/Surface/Desktop/antigravity
```

Завжди використовуй `/mnt/c/...` у WSL-терміналі.

---

## 3. Права на manage.sh

Якщо `manage.sh` не запускається через `./manage.sh`:
```bash
chmod +x manage.sh
./manage.sh start
```
Або просто: `bash manage.sh start` (без chmod)

---

## 4. Бот вже запущений (stale PID)

**Помилка:** `Bot is already running (PID: XXXXX)` але бот не відповідає.

```bash
# Перевірити чи реально запущений
bash manage.sh status

# Якщо PID файл "застарілий":
rm bot.pid
bash manage.sh start
```

**Або:** `bash manage.sh restart` — зупинить і запустить знову.

---

## 5. Конфлікт polling (getUpdates conflict)

**Помилка в логах:** `Conflict: terminated by other getUpdates request`

Значить запущено **два бота одночасно**!

```bash
# Знайти всі процеси бота
pgrep -f "python.*-m app.main"

# Вбити всі
pkill -f "python.*-m app.main"

# Почистити PID файл
rm -f bot.pid

# Запустити знову
bash manage.sh start
```

---

## 6. SQLite — файл БД не знайдено

**Помилка:** `unable to open database file`

Причина: бот запускається з неправильної директорії.

`manage.sh` автоматично робить `cd "$PROJECT_DIR"` — тому при запуску через нього все ок.

При ручному запуску — обов'язково бути в корені проекту:
```bash
cd /mnt/c/Users/Surface/Desktop/antigravity
./venv_linux/bin/python -m app.main
```

---

## 7. requirements.txt — asyncpg не потрібен для SQLite

У `requirements.txt` є `asyncpg==0.29.0` — це для PostgreSQL. Для SQLite він не використовується, але не заважає. Якщо він падає при установці на Ubuntu:

```bash
# Спробуй встановити без нього
./venv_linux/bin/pip install aiogram pydantic-settings SQLAlchemy alembic python-dotenv apscheduler aiosqlite pytest pytest-asyncio pytz
```

---

## 8. Змінна середовища PYTHONPATH

`manage.sh` автоматично встановлює:
```bash
export PYTHONPATH=/mnt/c/Users/Surface/Desktop/antigravity
```

Якщо запускаєш скрипти вручну і бачиш `ModuleNotFoundError: No module named 'app'`:
```bash
cd /mnt/c/Users/Surface/Desktop/antigravity
PYTHONPATH=$(pwd) ./venv_linux/bin/python scratch/list_all_services.py
```

---

## 9. Великий bot.log — очистити

```bash
# БЕЗПЕЧНО — тільки очистити, не видаляти
> bot.log

# Або залишити останні 1000 рядків
tail -n 1000 bot.log > bot.log.tmp && mv bot.log.tmp bot.log
```

---

## 10. Перевірити токен бота

```bash
# Перевірити .env
cat .env

# Або через Python
./venv_linux/bin/python check_env.py
```

---

## 11. BOT_TOKEN у .env не зчитується

Переконайся що `.env` знаходиться в корені проекту і формат правильний:
```env
BOT_TOKEN=1234567890:ABCDEFabcdef...
DATABASE_URL=sqlite+aiosqlite:///beauty_bot.db
```
> ❌ Без пробілів навколо `=`  
> ❌ Без лапок навколо значення  
> ❌ Без зайвих пустих рядків між змінними

---

## 12. Відновлення після збою

```bash
# 1. Зупинити все
pkill -f "python.*-m app.main"
rm -f bot.pid

# 2. Перевірити логи
tail -n 30 bot.log

# 3. Перевірити env
./venv_linux/bin/python check_env.py

# 4. Запустити знову
bash manage.sh start

# 5. Перевірити
bash manage.sh status
```
