from aiogram import Router
from ..cabinet import menu


def prepare_router() -> Router:
    router = Router()

    router.include_router(menu.prepare_router())

    return router
