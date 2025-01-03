from datetime import datetime


def get_date(raw_text):
    try:
        if raw_text == "Niet geregistreerd" or raw_text is None:
            return None
        return datetime.strptime(raw_text, "%d %B %Y").date()
    except (ValueError, TypeError):
        return None
