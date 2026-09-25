from unittest.mock import MagicMock, patch

from services.translation_service import TranslationService


def test_get_supported_languages_lists_six_pairs() -> None:
    languages = TranslationService.get_supported_languages()
    assert len(languages) == 6
    assert languages["English to Spanish"] == "Helsinki-NLP/opus-mt-en-es"


def test_translate_text_uses_the_right_model_and_decodes_output() -> None:
    fake_model = MagicMock()
    fake_model.tokenizer.return_value = {"input_ids": "encoded"}
    fake_model.model.generate.return_value = ["tokens"]
    fake_model.tokenizer.decode.return_value = "hola"

    with patch(
        "services.translation_service.TranslationModel.load_model",
        return_value=fake_model,
    ) as load_model:
        result = TranslationService.translate_text("hello", "English to Spanish")

    load_model.assert_called_once_with("Helsinki-NLP/opus-mt-en-es")
    assert result == "hola"
