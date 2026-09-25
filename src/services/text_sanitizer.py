import re

TAG_PATTERN = re.compile(r"[<>]")


class TextSanitizer:
    @staticmethod
    def sanitize_text(text: str) -> str:
        return TAG_PATTERN.sub("", text).strip()
