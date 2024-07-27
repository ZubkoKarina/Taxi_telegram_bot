from aiogram import Bot, Dispatcher
import asyncio
import sys
import logging
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from services.redis import redis_storage
from services.redis import RedisClient
from web_app.web_app import web_app
import uvicorn

from data.config import (
    WEBHOOK_ADDRESS,
    WEBHOOK_PATH,
    WEBHOOK_LISTENING_HOST,
    WEBHOOK_LISTENING_PORT,
    WEBHOOK_SECRET_TOKEN,
    BOT_TOKEN,
    WEB_APP_ADDRESS,
    WEB_APP_HOST,
    WEB_APP_PORT
)
from handlers import start, user
from bot import bot, dp


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.prepare_router())
    dp.include_router(user.prepare_router())


def setup_middlewares(dp: Dispatcher) -> None:
    pass


def setup_aiogram(dp: Dispatcher):
    print("Configuring aiogram")
    setup_handlers(dp)
    setup_middlewares(dp)
    print("Configured aiogram")


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        f"{WEBHOOK_ADDRESS}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET_TOKEN,
    )


async def delete_updates(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)


async def run_uvicorn():
    config = uvicorn.Config("web_app.web_app:web_app", host=WEB_APP_HOST, port=WEB_APP_PORT, reload=True)
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    loop = asyncio.new_event_loop()

    setup_aiogram(dp)

    # dp.startup.register(on_startup)

    # loop.run_until_complete(delete_updates(bot))

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET_TOKEN,
    )

    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    # web.run_app(app, host=WEBHOOK_LISTENING_HOST, port=WEBHOOK_LISTENING_PORT, loop=loop)
    redis_cli = RedisClient()
    # print(f'REDIS STATES: {redis_cli.get_all_states()}')
    await asyncio.gather(
        dp.start_polling(bot),
        run_uvicorn()
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
