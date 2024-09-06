from keyboards import inline, default


class KeyboardManager:
    def __init__(self):
        self.default = default.uk
        self.inline = inline.uk

    def init_language(self, language_code: str):
        if language_code == 'uk':
            self.default = default.uk
            self.inline = inline.uk
        elif language_code == 'ru':
            self.default = default.ru
            self.inline = inline.ru
        else:
            self.default = default.en
            self.inline = inline.en


def get_kb_manager(language_code: str):
    user_kb_manager = KeyboardManager()
    user_kb_manager.init_language(language_code)

    return user_kb_manager
