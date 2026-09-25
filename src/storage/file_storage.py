DEFAULT_TRANSLATIONS_PATH = "translations.txt"


class FileStorage:
    @staticmethod
    def save_translation(
        original_text: str,
        translated_text: str,
        language: str,
        path: str = DEFAULT_TRANSLATIONS_PATH,
    ) -> None:
        with open(path, "a") as f:
            f.write(
                f"Language: {language}\nOriginal Text: {original_text}\n"
                f"Translated Text: {translated_text}\n\n"
            )
