import logging
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Σύνδεση στη βάση δεδομένων
DATABASE_URL = "postgresql://users_info_6gu3_user:RFH4r8MZg0bMII5ruj5Gly9fwdTLAfSV@dpg-cr6vbghu0jms73ffc840-a/users_info_6gu3"
connection = psycopg2.connect(DATABASE_URL)
cursor = connection.cursor()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the bot! Use /create_account <username> <password> to create an account.\n"
        "Use /login <username> <password> to log in."
    )

async def create_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /create_account <username> <password>")
        return

    username, password = context.args
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        await update.message.reply_text("Username already exists. Please choose another one.")
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        await update.message.reply_text(f"Account created for {username}!")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /login <username> <password>")
        return

    username, password = context.args
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        await update.message.reply_text(f"Welcome back, {username}!")
    else:
        await update.message.reply_text("Invalid username or password. Please try again.")

if __name__ == '__main__':
    # Χρησιμοποιώντας το token που παρείχες
    application = ApplicationBuilder().token('7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create_account", create_account))
    application.add_handler(CommandHandler("login", login))

    # Ρύθμιση webhook
    webhook_url = "https://pythontestbot-f4g1.onrender.com"
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=f"{application.bot.token}",
        webhook_url=f"{webhook_url}/{application.bot.token}"
    )
