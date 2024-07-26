import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
from handlers.handlers import start
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == "__main__":
    main()
