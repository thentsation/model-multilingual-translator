from unittest.mock import patch

import pytest

from services.translation_workflow import EmptyTextError, process_translation


def test_empty_text_raises() -> None:
    with pytest.raises(EmptyTextError):
        process_translation("   ", "English to Spanish")


def test_process_translation_sanitizes_translates_and_saves() -> None:
    with (
        patch(
            "services.translation_workflow.TranslationService.translate_text",
            return_value="hola",
        ) as translate,
        patch("services.translation_workflow.FileStorage.save_translation") as save,
    ):
        result = process_translation("  hello  ", "English to Spanish")

    translate.assert_called_once_with("hello", "English to Spanish")
    save.assert_called_once_with("hello", "hola", "English to Spanish")
    assert result == "hola"
