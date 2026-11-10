from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core.memory import NexusMemory
from core.memory_engine import NexusMemoryEngine
from core.router import NexusRouter
from modules.llm import NexusLLM
from modules.web import NexusWeb


class NexusBrain:
    def __init__(self, session_id="default", chat_id="default", timezone="UTC"):
        self.name = "LIGHT BYTE"
        self.version = "6.0.0"

        self.memory = NexusMemory(f"{session_id}_{chat_id}")
        self.long_term_memory = NexusMemoryEngine(session_id)
        self.router = NexusRouter()
        self.llm = NexusLLM()
        self.web = NexusWeb()
        try:
            if not isinstance(timezone, str) or len(timezone) > 64:
                raise ValueError("Invalid timezone")
            ZoneInfo(timezone)
            self.timezone = timezone
        except (ValueError, TypeError, KeyError):
            self.timezone = "UTC"

    def _date_context(self):
        now = datetime.now(ZoneInfo(self.timezone))
        weekdays = (
            "понедельник", "вторник", "среда",
            "четверг", "пятница", "суббота", "воскресенье"
        )
        week_number = now.isocalendar().week
        week_type = "чётная" if week_number % 2 == 0 else "нечётная"
        return (
            "АКТУАЛЬНЫЕ ДАТА И ВРЕМЯ (системные данные сервера):\n"
            f"Дата: {now.strftime('%d.%m.%Y')}\n"
            f"Год: {now.year}\n"
            f"Месяц: {now.month}\n"
            f"Число: {now.day}\n"
            f"День недели: {weekdays[now.weekday()]}\n"
            f"Номер недели: {week_number}\n"
            f"Тип недели: {week_type}\n"
            f"Время: {now.strftime('%H:%M:%S')}\n"
            f"Часовой пояс: {self.timezone}\n"
            "Используй эти данные как источник текущей даты. "
            "Не угадывай дату и не подменяй её устаревшими сведениями."
        )

    def _calendar_answer(self, message):
        text = message.lower().strip()
        now = datetime.now(ZoneInfo(self.timezone))

        weekdays = (
            "понедельник", "вторник", "среда", "четверг",
            "пятница", "суббота", "воскресенье"
        )
        months = (
            "января", "февраля", "марта", "апреля",
            "мая", "июня", "июля", "августа",
            "сентября", "октября", "ноября", "декабря"
        )

        if any(x in text for x in (
            "сколько времени", "который час",
            "текущее время", "время сейчас"
        )):
            return f"Сейчас {now.strftime('%H:%M:%S')}. Часовой пояс: {self.timezone}."

        if "следующ" in text and "недел" in text:
            monday = now.date() - timedelta(days=now.weekday())
            target = monday + timedelta(weeks=1)
            iso = target.isocalendar()
            parity = "чётная" if iso.week % 2 == 0 else "нечётная"
            return f"Следующая неделя — ISO-неделя №{iso.week} ({parity}), начинается {target.strftime('%d.%m.%Y')}."

        if any(x in text for x in ("предыдущ", "прошл")) and "недел" in text:
            monday = now.date() - timedelta(days=now.weekday())
            target = monday - timedelta(weeks=1)
            iso = target.isocalendar()
            parity = "чётная" if iso.week % 2 == 0 else "нечётная"
            return f"Предыдущая неделя — ISO-неделя №{iso.week} ({parity}), начинается {target.strftime('%d.%m.%Y')}."

        if "недел" in text and any(x in text for x in (
            "какая", "номер", "чётн", "четн", "текущ", "сейчас"
        )):
            week = now.isocalendar().week
            parity = "чётная" if week % 2 == 0 else "нечётная"
            return f"Сейчас {week}-я календарная неделя ISO. Она {parity}."

        words = text.replace("?", "").replace("!", "").split()

        if "месяц" in words and "год" in words:
            return f"Сейчас {months[now.month - 1]} {now.year} года."

        if "месяц" in words:
            return f"Сейчас {months[now.month - 1]} {now.year} года."

        if "год" in words:
            return f"Сейчас {now.year} год."

        date_questions = (
            "какое сегодня число", "какая сегодня дата",
            "какой сегодня день", "какой день недели",
            "сегодняшняя дата"
        )

        if any(x in text for x in date_questions):
            weekday = weekdays[now.weekday()]
            month = months[now.month - 1]
            return f"Сегодня {weekday}, {now.day} {month} {now.year} года."

        return None

    def process(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()
        history = self.memory.get_history(limit=12)
        category = self.router.route(message)

        calendar_answer = self._calendar_answer(message)
        if calendar_answer is not None:
            self.memory.add("user", message)
            self.memory.add("assistant", calendar_answer)
            return {
                "name": self.name,
                "version": self.version,
                "category": category,
                "reply": calendar_answer
            }

        search_context = ""
        search_terms = (
            "найди", "поищи", "поиск", "википедия",
            "википедии", "в интернете"
        )

        if any(term in message.lower() for term in search_terms):
            search_data = self.web.search(message)

            if isinstance(search_data, dict):
                if search_data.get("status") == "success":
                    search_context = "\n".join(
                        f"{item.get('title', '')}: {item.get('text', '')}"
                        for item in search_data.get("results", [])
                    )

        memory_facts = self.long_term_memory.list_facts(limit=30)
        memory_lines = []

        for fact in memory_facts:
            memory_lines.append(
                f"[{fact['category']}] {fact['content']}"
            )

        context_parts = [self._date_context()]

        if memory_lines:
            context_parts.append(
                "Сохранённые факты о пользователе:\n"
                + "\n".join(memory_lines)
            )

        if search_context:
            context_parts.append(
                "Результаты веб-поиска:\n" + search_context
            )

        memory_context = "\n\n".join(context_parts)

        response = self.llm.generate(
            message,
            context=history,
            memory_context=memory_context
        )

        self.memory.add("user", message)
        self.memory.add("assistant", response)

        return {
            "name": self.name,
            "version": self.version,
            "category": category,
            "reply": response
        }

    def process_stream(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()
        history = self.memory.get_history(limit=12)
        category = self.router.route(message)

        calendar_answer = self._calendar_answer(message)
        if calendar_answer is not None:
            self.memory.add("user", message)
            self.memory.add("assistant", calendar_answer)
            yield calendar_answer
            return

        search_context = ""
        search_terms = (
            "найди", "поищи", "поиск", "википедия",
            "википедии", "в интернете"
        )

        if any(term in message.lower() for term in search_terms):
            search_data = self.web.search(message)
            if isinstance(search_data, dict):
                if search_data.get("status") == "success":
                    search_context = "\n".join(
                        f"{item.get('title', '')}: {item.get('text', '')}"
                        for item in search_data.get("results", [])
                    )

        memory_facts = self.long_term_memory.list_facts(limit=30)
        memory_lines = [
            f"[{fact['category']}] {fact['content']}"
            for fact in memory_facts
        ]

        context_parts = [f"Категория запроса: {category}", self._date_context()]

        if memory_lines:
            context_parts.append(
                "Сохранённые факты о пользователе:\n"
                + "\n".join(memory_lines)
            )

        if search_context:
            context_parts.append(
                "Результаты веб-поиска:\n" + search_context
            )

        memory_context = "\n\n".join(context_parts)
        answer_parts = []

        error_prefixes = (
            "Ошибка:",
            "Ошибка OpenRouter HTTP",
            "Превышено время ожидания",
            "Ошибка соединения",
            "Не удалось обработать",
            "Модель вернула пустой ответ"
        )

        for chunk in self.llm.generate_stream(
            message,
            context=history,
            memory_context=memory_context
        ):
            if not isinstance(chunk, str) or not chunk:
                continue

            if not answer_parts and chunk.strip().startswith(error_prefixes):
                raise RuntimeError(chunk.strip())

            answer_parts.append(chunk)
            yield chunk

        full_answer = "".join(answer_parts).strip()

        if not full_answer:
            raise RuntimeError("Модель не вернула ответ")

        self.memory.add("user", message)
        self.memory.add("assistant", full_answer)
