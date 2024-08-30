from flask import Flask, request
import telegram
import os

# Initialize Flask app
app = Flask(__name__)

# Use your actual token here
TOKEN = '7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE'
bot = telegram.Bot(token=TOKEN)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(), bot)
    chat_id = update.message.chat_id
    text = update.message.text

    if update.message:
        if text:
            user_name = text
            bot.send_message(chat_id=chat_id, text=f'Hello {user_name}!')
        else:
            bot.send_message(chat_id=chat_id, text='Tell me your name.')
    
    return 'ok'

@app.route('/')
def index():
    return 'Hello! The bot is running.'

if __name__ == '__main__':
    # Render will set the port for us
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
