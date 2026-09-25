from models.translation_model import TranslationModel

SUPPORTED_LANGUAGES: dict[str, str] = {
    "English to Spanish": "Helsinki-NLP/opus-mt-en-es",
    "Spanish to English": "Helsinki-NLP/opus-mt-es-en",
    "French to English": "Helsinki-NLP/opus-mt-fr-en",
    "English to French": "Helsinki-NLP/opus-mt-en-fr",
    "German to English": "Helsinki-NLP/opus-mt-de-en",
    "English to German": "Helsinki-NLP/opus-mt-en-de",
}


class TranslationService:
    @staticmethod
    def get_supported_languages() -> dict[str, str]:
        return SUPPORTED_LANGUAGES

    @staticmethod
    def translate_text(text: str, language: str) -> str:
        model_name = SUPPORTED_LANGUAGES[language]
        translation_model = TranslationModel.load_model(model_name)
        inputs = translation_model.tokenizer([text], return_tensors="pt")
        translated = translation_model.model.generate(**inputs)  # type: ignore[misc]
        return str(
            translation_model.tokenizer.decode(translated[0], skip_special_tokens=True)
        )
