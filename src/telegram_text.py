import re


_PICTURE_PLACEHOLDER_RE = re.compile(r"\*\*==>\s*picture\s*\[[^\]]*\]\s*intentionally omitted\s*<==\*\*")
_MULTISPACE_RE = re.compile(r"[ \t]{2,}")
_THREE_PLUS_NEWLINES_RE = re.compile(r"\n{3,}")


def sanitize_telegram_text(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""

    cleaned = _PICTURE_PLACEHOLDER_RE.sub("", cleaned)

    # We send plain text to Telegram, so strip common markdown symbols
    # that are often produced by the model and degrade readability.
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.replace("`", "")

    cleaned = _MULTISPACE_RE.sub(" ", cleaned)
    cleaned = _THREE_PLUS_NEWLINES_RE.sub("\n\n", cleaned)
    return cleaned.strip()
