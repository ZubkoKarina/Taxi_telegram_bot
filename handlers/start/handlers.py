from aiogram import types
from aiogram.fsm.context import FSMContext
from state.start import StartState
from state.register import RegisterState
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.http_client import HttpUser, HttpDriver, HttpOther
from handlers.common.helper import driver_cabinet_menu, user_cabinet_menu
from texts import TextManager, get_text_manager
from keyboards import KeyboardManager, get_kb_manager


async def greeting(message: types.Message, state: FSMContext):
    await state.clear()
    user_language = message.from_user.language_code

    user_text_manager: TextManager = get_text_manager(user_language)
    user_kb_manager: KeyboardManager = get_kb_manager(user_language)
    chat_id = message.chat.id

    response = await HttpDriver.get_driver_info({'chat_id': chat_id})
    if response.get('response_code') == 200:
        await HttpDriver.set_deactive_driver(data={'chat_id': chat_id})
        await state.set_data({'chat_id': chat_id, 'user_language': user_language})
        await driver_cabinet_menu(state, message=message)
        return

    response = await HttpUser.get_user_info({'chat_id': chat_id})
    user_data = response.get('response_data').get('data')

    if response.get('response_code') == 200:
        is_banned = user_data.get('is_banned')
        if is_banned:
            return await message.answer(user_text_manager.services.USER_BANNED)
        await state.set_data({'chat_id': chat_id, 'user_language': user_language})
        await user_cabinet_menu(state, message=message)
        return

    response_res = await HttpOther.get_text_greeting()

    # gif_url = response_res.get('response_data').get('data').get('gif')[0].get('link')
    # caption_text = response_res.get('response_data').get('data').get('desc')
    # await message.answer_animation(
    #     animation=gif_url,
    #     caption=caption_text,
    # )

    await message.answer(user_text_manager.asking.CHOOSE_LANGUAGE, reply_markup=user_kb_manager.inline.choose_language.choose_language)
    await state.set_state(StartState.waiting_language)


async def init_language(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    
    if callback.data == 'uk_language':
        await state.update_data(user_language='uk')
    if callback.data == 'ru_language':
        await state.update_data(user_language='ru')
    if callback.data == 'en_language':
        await state.update_data(user_language='en')

    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(text=user_text_manager.asking.PHONE, reply_markup=user_kb_manager.default.auth.phone_share)
    await callback.message.delete()

    await state.set_state(RegisterState.waiting_phone)