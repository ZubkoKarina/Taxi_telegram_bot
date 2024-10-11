from aiogram import Router
from handlers.common import ending_route
from handlers.common.helper import Handler, CallbackDataContainsKey


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(
            ending_route.ask_raw_message,
            []
        )
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router