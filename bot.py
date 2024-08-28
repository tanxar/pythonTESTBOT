from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from flask import Flask, request
import os

# Initialize Flask app
app = Flask(__name__)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, World!')

# Initialize Telegram bot application
bot_token = "7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE"
application = Application.builder().token(bot_token).build()
application.add_handler(CommandHandler("start", start))

# Define the route for webhook
@app.route(f'/{bot_token}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, application.bot)
    application.update_queue.put(update)
    return 'OK'

# Set webhook
def set_webhook():
    webhook_url = f"https://pythontestbot-f4g1.onrender.com/{bot_token}"
    application.bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=8080)
