from flask import Flask, request
import telegram
import logging
import os

# Initialize Flask app
app = Flask(__name__)

# Your actual Telegram bot token
TOKEN = '7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE'

# Initialize the bot
bot = telegram.Bot(token=TOKEN)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Webhook URL
WEBHOOK_URL = 'https://pythontestbot-f4g1.onrender.com/' + TOKEN

def set_webhook():
    """Sets the webhook for the bot."""
    try:
        response = bot.set_webhook(url=WEBHOOK_URL)
        if response:
            logging.info("Webhook set successfully.")
        else:
            logging.error("Failed to set webhook.")
    except Exception as e:
        logging.error(f"Error setting webhook: {e}")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        # Parse the incoming update from Telegram using Flask's request
        update = telegram.Update.de_json(request.get_json(), bot)
        chat_id = update.message.chat_id
        text = update.message.text

        logging.info(f"Received message: '{text}' from chat ID: {chat_id}")

        if update.message:
            if text:
                user_name = text
                bot.send_message(chat_id=chat_id, text=f'Hello {user_name}!')
                logging.info(f"Sent message: 'Hello {user_name}!' to chat ID: {chat_id}")
            else:
                bot.send_message(chat_id=chat_id, text='Tell me your name.')
                logging.info(f"Sent message: 'Tell me your name.' to chat ID: {chat_id}")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    return 'ok'

@app.route('/')
def index():
    return 'Hello! The bot is running.'

if __name__ == '__main__':
    # Set webhook when starting the app
    set_webhook()
    
    # Render will set the port for us
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
