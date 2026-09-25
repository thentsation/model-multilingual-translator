from storage.file_storage import FileStorage


def test_save_translation_appends_entry(tmp_path) -> None:
    path = tmp_path / "translations.txt"

    FileStorage.save_translation("hello", "hola", "English to Spanish", path=str(path))
    FileStorage.save_translation("bye", "adios", "English to Spanish", path=str(path))

    content = path.read_text()
    assert content.count("Language: English to Spanish") == 2
    assert "Original Text: hello" in content
    assert "Translated Text: hola" in content
