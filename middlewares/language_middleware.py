from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from texts import TextManager
from keyboards import KeyboardManager

class LanguageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Отримуємо FSMContext з data
        state: FSMContext = data['state']
        state_data = await state.get_data()

        # Визначаємо мову користувача, якщо немає, то використовуємо 'uk' за замовчуванням
        user_language = state_data.get('user_language', 'uk')

        # Зберігаємо тільки серіалізований код мови в контексті стану
        await state.update_data(user_language=user_language)

        # Ініціалізуємо TextManager і KeyboardManager
        user_text_manager = TextManager()
        user_kb_manager = KeyboardManager()
        user_text_manager.init_language(language_code=user_language)
        user_kb_manager.init_language(language_code=user_language)

        # Додаємо об'єкти в дані обробника
        data['user_text_manager'] = user_text_manager
        data['user_kb_manager'] = user_kb_manager

        # Викликаємо наступний обробник
        return await handler(event, data)
