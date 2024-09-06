from aiogram import Router, F
from handlers.start import handlers
from aiogram.filters import CommandStart
from handlers.common.helper import Handler
from state.start import StartState


def prepare_router() -> Router:

    router = Router()
    # Start
    message_list = [
        Handler(handlers.greeting, [CommandStart()]),
    ]

    callback_list = [
        Handler(
            handlers.init_language, [StartState.waiting_language, F.data == 'en_language']
        ),
        Handler(
            handlers.init_language, [StartState.waiting_language, F.data == 'uk_language']
        ),
        Handler(
            handlers.init_language, [StartState.waiting_language, F.data == 'ru_language']
        ),
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    return router

