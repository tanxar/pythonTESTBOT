from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Your Telegram Bot Token
TELEGRAM_TOKEN = '7403620437:AAHUzMiWQt_AHAZ-PwYY0spVfcCKpWFKQoE'
WEBHOOK_URL = 'https://pythontestbot-f4g1.onrender.com/webhook'

# In-memory user storage
users = {}
sessions = {}

def send_message(chat_id, text, reply_markup=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        data['reply_markup'] = reply_markup
    requests.post(url, json=data)

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}'
    response = requests.get(url)
    return jsonify(response.json())

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    message = data['message']
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    # Handle start command
    if text == '/start':
        reply_markup = {
            'keyboard': [['Create account'], ['Login']],
            'one_time_keyboard': True
        }
        send_message(chat_id, "Welcome! Choose an option:", reply_markup)
        return jsonify({'status': 'ok'})

    # Handle login option
    if text.lower() == 'login':
        sessions[chat_id] = {'step': 'awaiting_username'}
        send_message(chat_id, "Please enter your username:")
        return jsonify({'status': 'ok'})

    # Handle login username
    if chat_id in sessions and sessions[chat_id]['step'] == 'awaiting_username':
        sessions[chat_id]['username'] = text
        sessions[chat_id]['step'] = 'awaiting_password'
        send_message(chat_id, "Please enter your password:")
        return jsonify({'status': 'ok'})

    # Handle login password
    if chat_id in sessions and sessions[chat_id]['step'] == 'awaiting_password':
        username = sessions[chat_id].get('username')
        password = text
        if username and username not in users:
            users[username] = password  # Register the user
            del sessions[chat_id]
            send_message(chat_id, "Login successful!")
        elif username and users.get(username) == password:
            del sessions[chat_id]
            send_message(chat_id, "Login successful!")
        else:
            send_message(chat_id, "Invalid username or password.")
        return jsonify({'status': 'ok'})

    # Handle other messages
    send_message(chat_id, "Please choose an option from the keyboard.")
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
