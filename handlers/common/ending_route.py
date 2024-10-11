from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
from keyboards import KeyboardManager, get_kb_manager
from texts import TextManager, get_text_manager


async def ask_raw_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(text=user_text_manager.asking.RAW_MASSAGE)