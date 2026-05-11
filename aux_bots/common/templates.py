import html

def format_post(data: dict, bot_type: str) -> str:
    """
    Formats the post based on the collected data and bot type.
    """
    if bot_type == "vacancy":
        header = "🆕 <b>НОВА ВАКАНСІЯ</b>\n\n"
        fields = [
            ("🏢 Посада:", data.get("position")),
            ("💼 Компанія:", data.get("company")),
            ("💰 Зарплата:", data.get("salary")),
            ("📍 Локація:", data.get("location")),
            ("📝 Вимоги:", data.get("requirements")),
            ("📞 Контакти:", data.get("contact")),
        ]
    else:  # model
        header = "💅 <b>ШУКАЮ МОДЕЛЬ</b>\n\n"
        fields = [
            ("💅 Послуга:", data.get("service")),
            ("📅 Дата/Час:", data.get("datetime")),
            ("📍 Локація:", data.get("location")),
            ("📝 Вимоги:", data.get("requirements")),
            ("💵 Вартість:", data.get("price")),
            ("📞 Контакти:", data.get("contact")),
        ]

    lines = [header]
    for label, value in fields:
        if value:
            # Escape HTML to prevent injection issues
            safe_value = html.escape(str(value))
            lines.append(f"<b>{label}</b> {safe_value}")
    
    return "\n".join(lines)
