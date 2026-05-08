import deepl

class DeepLTranslator:
    def __init__(self, auth_key):
        self.translator = deepl.Translator(auth_key)

    def translate_text(self, text, target_lang="UK"):
        try:
            result = self.translator.translate_text(text, target_lang=target_lang)
            print(f"Оригинал: {text}")
            print(f"Перевод: {result.text}")
            print(f"Определенный язык оригинала: {result.detected_source_lang}")
            return result.text
        except deepl.DeepLException as e:
            print(f"Ошибка DeepL: {e}")
