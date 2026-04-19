# 🐧 Налаштування Ubuntu/WSL2 — Перший запуск

## Крок 1 — Відкрити Ubuntu/WSL2

**Варіант A:** через Windows Terminal  
```
Windows Terminal → вибрати "Ubuntu" у вкладці
```

**Варіант B:** через VS Code  
```
Ctrl+` → у терміналі натисни кнопку "+" → вибрати "Ubuntu (WSL)"
```

**Так виглядає правильний термінал WSL:**
```bash
username@DESKTOP-XXXXX:~$
```
> ❌ Якщо бачиш `PS C:\Users\...>` — це PowerShell, не WSL!

---

## Крок 2 — Перейти до папки проекту

```bash
cd /mnt/c/Users/Surface/Desktop/antigravity
```

> 💡 Диск C: у WSL монтується як `/mnt/c/`

**Перевірити що ти в правильній папці:**
```bash
ls
# Повинен побачити: app/ manage.sh requirements.txt .env ...
```

---

## Крок 3 — Перевірити/Створити venv_linux

```bash
# Перевірити чи існує
ls venv_linux/bin/python

# Якщо НЕ існує — створити:
python3 -m venv venv_linux

# Встановити залежності
./venv_linux/bin/pip install -r requirements.txt
```

> ⚠️ **Важливо:** `venv_linux` — окремий від `venv` (Windows). Вони несумісні!  
> `venv` → для Windows  
> `venv_linux` → для WSL/Ubuntu

---

## Крок 4 — Запустити бота

```bash
# Спосіб 1: через manage.sh (рекомендовано)
bash manage.sh start

# Спосіб 2: напряму через venv_linux
./venv_linux/bin/python -m app.main
```

---

## Крок 5 — Перевірити що бот запустився

```bash
bash manage.sh status
# або
bash manage.sh logs
```

---

## 🔁 Щоденний воркфлоу

```bash
cd /mnt/c/Users/Surface/Desktop/antigravity
bash manage.sh start    # Запустити
bash manage.sh status   # Перевірити
bash manage.sh logs     # Дивитись логи
bash manage.sh stop     # Зупинити
bash manage.sh restart  # Рестартувати
```

---

## 🚀 Швидкий старт (aliases)

Додай до `~/.bashrc` (виконай один раз):

```bash
echo '
# Antigravity Bot shortcuts
BOT_DIR="/mnt/c/Users/Surface/Desktop/antigravity"
alias bot="cd $BOT_DIR && bash manage.sh"
alias bot-start="cd $BOT_DIR && bash manage.sh start"
alias bot-stop="cd $BOT_DIR && bash manage.sh stop"
alias bot-status="cd $BOT_DIR && bash manage.sh status"
alias bot-logs="cd $BOT_DIR && bash manage.sh logs"
alias bot-restart="cd $BOT_DIR && bash manage.sh restart"
' >> ~/.bashrc

source ~/.bashrc
```

Після цього можна просто писати:
```bash
bot-start    # Запустити
bot-stop     # Зупинити
bot-status   # Статус
bot-logs     # Логи
bot-restart  # Рестарт
```
