from pyexpat.errors import messages

from bot import dp, bot
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from bot import bot


async def delete_messages(name_message_list: str, state: FSMContext, name_msg: str = None):
    data = await state.get_data()
    message_list = data.get(name_message_list, [])

    remaining_messages = []

    for message in message_list:
        chat_id = message['chat_id']
        message_id = message['message_id']
        message_name = message.get('name')

        if name_msg is not None and message_name != name_msg:
            remaining_messages.append(message)
            continue

        try:
            await bot.delete_message(chat_id, message_id)
            print(f"Видалено повідомлення {message_id} у чаті {chat_id} з ім'ям {message_name}")
        except Exception as e:
            print(f"Не вдалося видалити повідомлення {message_id} у чаті {chat_id}: {str(e)}")
            remaining_messages.append(message)

    await state.update_data({name_message_list: remaining_messages})


async def add_to_message_list(message: types.Message, state: FSMContext, name_message_list: str, name_msg: str = None):
    data = await state.get_data()

    message_list: list = data.get(name_message_list)

    if message_list is None:
        message_list = []

    message_list.append({'message_id': message.message_id, 'chat_id': message.chat.id, 'name': name_msg})

    await state.update_data({name_message_list: message_list})

    return True


async def find_message_in_list(state: FSMContext, name_message_list: str, name_msg: str = None, chat_id: int = None) -> bool:
    data = await state.get_data()

    message_list = data.get(name_message_list, [])
    for message in message_list:
        if message.get('name') == name_msg:
            return True
        if chat_id:
            if int(message.get('chat_id')) == int(chat_id):
                return True

    return False


async def mass_send_message(text: str, chat_id_list: list):
    for chat_id in chat_id_list:
        await bot.send_message(text=text, chat_id=chat_id)

