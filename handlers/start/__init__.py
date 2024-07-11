from aiogram import Router, F
from handlers.start import handlers
from aiogram.filters import CommandStart
from handlers.common.helper import Handler


def prepare_router() -> Router:

    router = Router()
    # Start
    message_list = [
        Handler(handlers.greeting, [CommandStart()]),
    ]
    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

