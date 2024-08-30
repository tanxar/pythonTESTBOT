import os
import psycopg2
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

app = Flask(__name__)

# Telegram bot token
TELEGRAM_TOKEN = '7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE'
bot = Bot(token=TELEGRAM_TOKEN)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://users_info_6gu3_user:RFH4r8MZg0bMII5ruj5Gly9fwdTLAfSV@dpg-cr6vbghu0jms73ffc840-a/users_info_6gu3')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Helper function to create users table if it doesn't exist
def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            balance INTEGER DEFAULT 0
        );
    """)
    conn.commit()

# Start Command
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Create Account", callback_data='create_account')],
        [InlineKeyboardButton("Login", callback_data='login')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Handle button press
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'create_account':
        query.message.reply_text("Please choose a username:")
        context.user_data['action'] = 'create_account'

    elif query.data == 'login':
        query.message.reply_text("Please enter your username:")
        context.user_data['action'] = 'login'

# Handle messages (username/password input)
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    action = context.user_data.get('action')

    if action == 'create_account':
        cursor.execute("SELECT * FROM users WHERE username = %s", (text,))
        if cursor.fetchone():
            update.message.reply_text("Username taken, please choose another:")
        else:
            context.user_data['username'] = text
            update.message.reply_text("Please choose a password:")
            context.user_data['action'] = 'create_password'

    elif action == 'create_password':
        username = context.user_data.get('username')
        password = text
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        update.message.reply_text(f"Account created successfully for {username} with balance 0!")
        context.user_data.clear()

    elif action == 'login':
        username = text
        context.user_data['username'] = username
        update.message.reply_text("Please enter your password:")
        context.user_data['action'] = 'login_password'

    elif action == 'login_password':
        username = context.user_data.get('username')
        password = text
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        if cursor.fetchone():
            update.message.reply_text(f"Login successful! Welcome back, {username}!")
            context.user_data.clear()
        else:
            update.message.reply_text("Username or password incorrect, please try again:")
            context.user_data['action'] = 'login'

# Webhook route
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Set webhook on startup
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    webhook_url = f"https://pythontestbot-f4g1.onrender.com/{TELEGRAM_TOKEN}"
    bot.set_webhook(url=webhook_url)
    return "Webhook set"

if __name__ == "__main__":
    init_db()
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
