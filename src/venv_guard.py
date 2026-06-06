import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_VENV_DIR = _PROJECT_ROOT / ".venv"


def ensure_virtualenv() -> None:
    if sys.prefix == sys.base_prefix:
        _exit_with_hint()

    if not _VENV_DIR.is_dir():
        _exit_with_hint("Каталог .venv не найден в корне проекта.")

    if Path(sys.prefix).resolve() != _VENV_DIR.resolve():
        _exit_with_hint("Активируйте виртуальное окружение проекта: source .venv/bin/activate")


def _exit_with_hint(extra: str = "") -> None:
    lines = [
        "Запуск возможен только внутри проектного виртуального окружения .venv.",
        "Создайте окружение и зависимости: make install",
        "Запустите бота: make run",
    ]
    if extra:
        lines.insert(1, extra)
    raise SystemExit("\n".join(lines))
