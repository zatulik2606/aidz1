import unittest

from src.telegram_text import sanitize_telegram_text


class TelegramTextTests(unittest.TestCase):
    def test_sanitize_removes_markdown_markers(self) -> None:
        text = "**Жирный** и `код` и __подчеркнуто__"
        result = sanitize_telegram_text(text)
        self.assertEqual(result, "Жирный и код и подчеркнуто")

    def test_sanitize_removes_picture_placeholders(self) -> None:
        text = "Начало\n**==> picture [100 x 100] intentionally omitted <==**\nКонец"
        result = sanitize_telegram_text(text)
        self.assertEqual(result, "Начало\n\nКонец")
