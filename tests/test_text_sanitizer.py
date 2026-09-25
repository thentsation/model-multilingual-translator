from services.text_sanitizer import TextSanitizer


def test_strips_angle_brackets() -> None:
    assert TextSanitizer.sanitize_text("<script>hi</script>") == "scripthi/script"


def test_strips_surrounding_whitespace() -> None:
    assert TextSanitizer.sanitize_text("  hello world  ") == "hello world"


def test_empty_or_whitespace_only_becomes_empty_string() -> None:
    assert TextSanitizer.sanitize_text("   ") == ""
