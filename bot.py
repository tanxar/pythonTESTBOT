from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, World!')

def main() -> None:
    # Create the application and pass it the bot token
    application = Application.builder().token("7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE").build()

    # Register the start command handler
    application.add_handler(CommandHandler("start", start))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
