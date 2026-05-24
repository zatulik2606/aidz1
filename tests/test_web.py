import asyncio
import unittest
from unittest.mock import patch

from src.tools.web import web_search


class WebSearchTests(unittest.TestCase):
    @patch("src.tools.web.load_config")
    def test_web_search_without_api_key(self, mock_load_config) -> None:
        mock_load_config.return_value = type("Cfg", (), {"tavily_api_key": ""})()
        result = asyncio.run(web_search("проверка"))
        self.assertEqual(result, "Веб-поиск недоступен: не задан TAVILY_API_KEY.")

    @patch("src.tools.web.load_config")
    @patch("src.tools.web._perform_tavily_request")
    def test_web_search_returns_formatted_results(
        self,
        mock_request,
        mock_load_config,
    ) -> None:
        mock_load_config.return_value = type("Cfg", (), {"tavily_api_key": "key"})()
        mock_request.return_value = {
            "results": [
                {
                    "title": "Python 3.12 Released",
                    "url": "https://example.com/python-3-12",
                    "content": "Python 3.12 introduces performance improvements.",
                }
            ]
        }

        result = asyncio.run(web_search("python 3.12 release date"))
        self.assertIn("Найдено в интернете:", result)
        self.assertIn("Python 3.12 Released", result)
        self.assertIn("https://example.com/python-3-12", result)
