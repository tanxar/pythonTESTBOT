import os
import psycopg2
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Initialize Flask app
app = Flask(__name__)

# Database connection setup
DATABASE_URL = "postgresql://users_info_6gu3_user:RFH4r8MZg0bMII5ruj5Gly9fwdTLAfSV@dpg-cr6vbghu0jms73ffc840-a/users_info_6gu3"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Initialize Telegram bot application
TOKEN = "7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE"
WEBHOOK_URL = 'https://pythontestbot-f4g1.onrender.com/' + TOKEN
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Create Account", callback_data='create_account'),
            InlineKeyboardButton("Login", callback_data='login')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)

# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'create_account':
        await query.message.reply_text('Choose a username:')
        context.user_data['process'] = 'create_account'
    elif query.data == 'login':
        await query.message.reply_text('Enter your username:')
        context.user_data['process'] = 'login'

# Handle text input based on the user's process
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    process = context.user_data.get('process')

    if process == 'create_account':
        await handle_create_account(update, context)
    elif process == 'create_password':
        await create_password(update, context)
    elif process == 'login':
        await handle_login(update, context)
    elif process == 'check_password':
        await check_password(update, context)
    else:
        await update.message.reply_text("Unknown state. Please start over by pressing 'Start'.")

# Handle account creation
async def handle_create_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.text
    print(f"Received username for account creation: {username}")  # Debugging line
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    result = cur.fetchone()

    if result:
        await update.message.reply_text("Username taken, choose another username:")
    else:
        context.user_data['username'] = username
        await update.message.reply_text("Username available. Choose a password:")
        context.user_data['process'] = 'create_password'

# Handle password creation for new account
async def create_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    password = update.message.text
    username = context.user_data.get('username')
    print(f"Creating account with username: {username} and password: {password}")  # Debugging line
    cur.execute("INSERT INTO users (username, password, balance) VALUES (%s, %s, %s)", (username, password, 0))
    conn.commit()
    await update.message.reply_text("Account created successfully!")
    context.user_data.clear()

# Handle login process
async def handle_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.text
    print(f"Received username for login: {username}")  # Debugging line
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    result = cur.fetchone()

    if not result:
        await update.message.reply_text("Username does not exist, enter a valid username:")
    else:
        context.user_data['username'] = username
        await update.message.reply_text("Username found. Enter your password:")
        context.user_data['process'] = 'check_password'

# Handle password checking during login
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    password = update.message.text
    username = context.user_data.get('username')
    print(f"Checking password for username: {username}")  # Debugging line
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    result = cur.fetchone()

    if not result:
        await update.message.reply_text("Username or password not correct, enter your username again:")
        context.user_data['process'] = 'login'
    else:
        await update.message.reply_text("Login successful!")
        context.user_data.clear()

# Flask route for the root URL
@app.route('/')
def index():
    return "Hello, World"

# Flask route for handling Telegram webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), app_telegram.bot)
    app_telegram.process_update(update)
    return "ok"

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update} caused error {context.error}')

# Set up Telegram bot handlers
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CallbackQueryHandler(button_handler))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app_telegram.add_error_handler(error)

# Main entry point for the Flask app
if __name__ == '__main__':
    # Set up webhook
    app_telegram.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)))
