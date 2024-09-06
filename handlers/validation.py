from aiogram import types
from aiogram.fsm.context import FSMContext
from texts import TextManager, get_text_manager


async def not_valid_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await message.answer(user_text_manager.validation.NOT_VALID_TEXT)
    await message.answer(user_text_manager.asking.TRY_AGAIN)


async def not_valid_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await message.answer(user_text_manager.validation.NOT_VALID_NUMBER)
    await message.answer(user_text_manager.asking.TRY_AGAIN)
