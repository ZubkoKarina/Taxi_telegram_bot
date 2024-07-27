from environs import Env

env = Env()

env.read_env()

BOT_TOKEN: str = env.str("TELEGRAM_BOT_TOKEN")
BOT_URL: str = env.str("TELEGRAM_BOT_LINK")

WEB_APP_ADDRESS: str = env.str("WEB_APP_ADDRESS")
WEB_APP_PORT: int = env.int("WEB_APP_PORT")
WEB_APP_HOST: str = env.str("WEB_APP_HOST")

WEBHOOK_ADDRESS: str = env.str("TELEGRAM_WEBHOOK_ADDRESS")
WEBHOOK_SECRET_TOKEN: str = env.str("TELEGRAM_WEBHOOK_SECRET_TOKEN")
WEBHOOK_LISTENING_HOST: str = env.str("TELEGRAM_WEBHOOK_LISTENING_HOST")
WEBHOOK_LISTENING_PORT: int = env.int("TELEGRAM_WEBHOOK_LISTENING_PORT")
WEBHOOK_PATH: str = env.str("TELEGRAM_WEBHOOK_PATH")

FSM_HOST: str = env.str("FSM_HOST")
FSM_PORT: int = env.int("FSM_PORT")
FSM_PASSWORD: str = env.str("FSM_PASSWORD")

API_URL: str = env.str('API_URL')
API_KEY: str = env.str('API_KEY')

API_KEY_GOOGLE_MAP: str = env.str('API_KEY_GOOGLE_MAPS')
