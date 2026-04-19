
import re
from datetime import datetime

def parse_datetime_flexible(text: str) -> datetime:
    """
    Витягує цифри з тексту та намагається побудувати дату.
    Підтримує формати:
    - 14.04 12:00
    - 14 04 12 00
    - 14.4 12 0
    - 14041200
    """
    # Знаходимо всі групи цифр
    parts = re.findall(r'\d+', text)
    
    # Якщо одна довга строка цифр (наприклад 14041200)
    if len(parts) == 1 and len(parts[0]) >= 7:
        s = parts[0]
        if len(s) == 7: # наприклад 1441200 -> спробуємо вставити 0 перед 4
            # Це ризиковано, краще просити 8 цифр або розділювачі
            pass 
        digits = s
    else:
        # Доповнюємо кожну частину нулем зліва, якщо вона одноцифрова
        # (для днів, місяців, годин, хвилин)
        padded_parts = [p.zfill(2) if len(p) == 1 else p for p in parts]
        digits = "".join(padded_parts)

    # Беремо перші 8 цифр
    if len(digits) < 6: # Мінімум день, місяць, година
        raise ValueError("Замало цифр для розпізнавання дати")

    # Доповнюємо хвилини нулями, якщо їх немає
    if len(digits) == 6:
        digits += "00"
    
    clean_digits = digits[:8]
    
    try:
        dt = datetime.strptime(clean_digits, "%d%m%H%M")
        return dt.replace(year=datetime.now().year)
    except ValueError as e:
        raise ValueError(f"Невірний формат дати: {text}") from e
