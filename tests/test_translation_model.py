from unittest.mock import MagicMock, patch

from models.translation_model import TranslationModel


def test_load_model_caches_by_name() -> None:
    TranslationModel._model_cache.clear()
    with (
        patch("models.translation_model.MarianTokenizer") as tokenizer_cls,
        patch("models.translation_model.MarianMTModel") as model_cls,
    ):
        tokenizer_cls.from_pretrained.return_value = MagicMock()
        model_cls.from_pretrained.return_value = MagicMock()

        first = TranslationModel.load_model("fake-model")
        second = TranslationModel.load_model("fake-model")

        assert first is second
        tokenizer_cls.from_pretrained.assert_called_once_with("fake-model")
        model_cls.from_pretrained.assert_called_once_with("fake-model")
