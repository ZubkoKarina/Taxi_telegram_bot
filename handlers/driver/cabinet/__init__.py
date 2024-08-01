from aiogram import Router
from ..cabinet import menu
from ..cabinet import order
from ..cabinet import setting


def prepare_router() -> Router:
    router = Router()

    router.include_router(menu.prepare_router())
    router.include_router(order.prepare_router())
    router.include_router(setting.prepare_router())

    return router
