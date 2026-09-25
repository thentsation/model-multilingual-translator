import logging

from services.text_sanitizer import TextSanitizer
from services.translation_service import TranslationService
from storage.file_storage import FileStorage


class EmptyTextError(ValueError):
    pass


def process_translation(
    text: str, language: str, logger: logging.Logger | None = None
) -> str:
    logger = logger or logging.getLogger("Translator")

    sanitized_text = TextSanitizer.sanitize_text(text)
    if not sanitized_text:
        raise EmptyTextError("Please enter a valid text to translate.")

    translated_text = TranslationService.translate_text(sanitized_text, language)
    FileStorage.save_translation(sanitized_text, translated_text, language)
    logger.info("Translated text (language: %s)", language)
    return translated_text
