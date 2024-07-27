from aiogram import Router, F
from handlers.user.auth import register
from handlers.common.helper import Handler
from state.register import RegisterState


def prepare_router() -> Router:

    router = Router()
    # Start
    message_list = [
        Handler(register.save_phone, [RegisterState.waiting_phone, F.contact]),
        Handler(register.save_name, [RegisterState.waiting_name, F.text]),
        Handler(register.save_region, [RegisterState.waiting_region, F.text]),
        Handler(register.save_city, [RegisterState.waiting_city, F.text]),
    ]
    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

