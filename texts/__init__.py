from texts.uk import asking as ua_asking, start as ua_start, services as ua_services, keyboards as ua_keyboards, \
    validation as ua_validation
from texts.ru import asking as ru_asking, start as ru_start, services as ru_services, keyboards as ru_keyboards, \
    validation as ru_validation
from texts.en import asking as eng_asking, start as eng_start, services as eng_services, keyboards as eng_keyboards, \
    validation as eng_validation
from aiogram import types


class TextManager:
    def __init__(self):
        self.validation = ua_validation
        self.asking = ua_asking
        self.start = ua_start
        self.services = ua_services
        self.keyboards = ua_keyboards

    def init_language(self, language_code: str):
        if language_code == 'uk':
            self.asking = ua_asking
            self.start = ua_start
            self.services = ua_services
            self.keyboards = ua_keyboards
            self.validation = ua_validation
        elif language_code == 'ru':
            self.asking = ru_asking
            self.start = ru_start
            self.services = ru_services
            self.keyboards = ru_keyboards
            self.validation = ru_validation
        else:
            self.asking = eng_asking
            self.start = eng_start
            self.services = eng_services
            self.keyboards = eng_keyboards
            self.validation = eng_validation


def filter_text(kb_text: str):
    def filter_func(message: types.Message) -> bool:
        uk_text = getattr(ua_keyboards, kb_text, None)
        ru_text = getattr(ru_keyboards, kb_text, None)
        en_text = getattr(eng_keyboards, kb_text, None)
        return message.text in [uk_text, en_text, ru_text]

    return filter_func


def get_text_manager(language_code: str):
    user_text_manager = TextManager()
    user_text_manager.init_language(language_code)

    return user_text_manager
