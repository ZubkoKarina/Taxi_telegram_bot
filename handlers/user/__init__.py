from aiogram import Router
from handlers.user import auth as user_auth
from handlers.user import cabinet as user_cabinet


def prepare_router() -> Router:
    router = Router()

    router.include_router(user_auth.prepare_router())
    router.include_router(user_cabinet.prepare_router())

    return router
