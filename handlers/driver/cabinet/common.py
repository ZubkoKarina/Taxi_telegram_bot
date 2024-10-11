from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from handlers.common.helper import driver_cabinet_menu
from state.driver import OrderDriver
from texts import TextManager, get_text_manager


async def callback_open_menu(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if callback.message and callback.message.chat:  # Перевірка на наявність callback.message та chat
        chat_id = callback.message.chat.id
    else:
        chat_id = callback.from_user.id  # Якщо message немає, використовуємо ID користувача

    await driver_cabinet_menu(state=state, chat_id=chat_id, bot=bot)

    if callback.message:
        await callback.message.delete()

    await callback.answer()


async def open_menu(message: types.Message, state: FSMContext):
    await driver_cabinet_menu(state, message=message)


async def open_order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.ORDER_MENU, reply_markup=ReplyKeyboardRemove())

    await state.set_state(OrderDriver.waiting_menu_order)
