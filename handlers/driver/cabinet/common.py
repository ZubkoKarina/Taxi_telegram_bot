from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from handlers.common.helper import driver_cabinet_menu


async def callback_open_menu(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await driver_cabinet_menu(state=state, bot=bot, chat_id=callback.from_user.id)

    if callback.message:
        await callback.message.delete()

    await callback.answer()


async def open_menu(message: types.Message, state: FSMContext):
    await driver_cabinet_menu(state, message=message)
