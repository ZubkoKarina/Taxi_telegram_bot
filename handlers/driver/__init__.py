from aiogram import Router
from handlers.driver import cabinet as driver_cabinet


def prepare_router() -> Router:
    router = Router()

    router.include_router(driver_cabinet.prepare_router())

    return router
