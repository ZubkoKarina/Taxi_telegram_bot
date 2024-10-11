from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from handlers.common.helper import user_cabinet_menu
from keyboards import KeyboardManager, get_kb_manager
from texts import TextManager, get_text_manager
from state.user import OrderTaxi


async def callback_open_menu(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await user_cabinet_menu(state=state, message=callback.message)

    if callback.message:
        await callback.message.delete()

    await callback.answer()


async def open_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)


async def open_order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.ORDER_MENU, reply_markup=user_kb_manager.default.users.order_menu)

    await state.set_state(OrderTaxi.waiting_menu_order)