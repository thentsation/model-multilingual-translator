import streamlit as st

from logger import setup_logging
from services.translation_service import TranslationService
from services.translation_workflow import EmptyTextError, process_translation


def main() -> None:
    logger = setup_logging()
    st.title("Multilingual Translator")

    languages = TranslationService.get_supported_languages()
    selected_language = st.selectbox(
        "Select translation language:", list(languages.keys())
    )

    original_text = st.text_area(
        "Enter text for translation (max 500 characters):", max_chars=500, height=150
    )

    if st.button("Translate"):
        try:
            translated_text = process_translation(
                original_text, selected_language, logger
            )
        except EmptyTextError:
            st.warning("Please enter a valid text to translate.")
            return
        except Exception as e:
            logger.exception("Translation failed")
            st.error(f"An error occurred during translation: {e}")
            return

        st.success("Translation completed:")
        st.write(translated_text)
        st.info("The translation was saved successfully.")

        if st.checkbox("Was the translation helpful?"):
            st.success("Thank you for your feedback!")
        else:
            st.info("Please let us know how we can improve.")


if __name__ == "__main__":
    main()
