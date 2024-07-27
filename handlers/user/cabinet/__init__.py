from aiogram import Router
from ..cabinet import menu
from ..cabinet import edit_user
from ..cabinet import other
from ..cabinet import order
from ..cabinet import become_driver


def prepare_router() -> Router:
    router = Router()

    router.include_router(menu.prepare_router())
    router.include_router(edit_user.prepare_router())
    router.include_router(other.prepare_router())
    router.include_router(order.prepare_router())
    router.include_router(become_driver.prepare_router())

    return router
