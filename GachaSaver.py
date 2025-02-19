import os
import requests
from telegram import Bot
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Dictionary to store user IDs and their game IDs
user_data = {}

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Use /add <game_id> to add a game ID.')

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    game_id = ' '.join(context.args)
    if user_id not in user_data:
        user_data[user_id] = []
    user_data[user_id].append(game_id)
    await update.message.reply_text(f'Added game ID: {game_id}')

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    game_id = ' '.join(context.args)
    if user_id in user_data and game_id in user_data[user_id]:
        user_data[user_id].remove(game_id)
        await update.message.reply_text(f'Deleted game ID: {game_id}')
    else:
        await update.message.reply_text(f'Game ID: {game_id} not found')

async def myids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_data:
        game_ids = "\n".join(user_data[user_id])
        await update.message.reply_text(f'Your game IDs:\n{game_ids}')
    else:
        await update.message.reply_text('You have no game IDs stored.')

# Webhook route
@app.route('/webhook', methods=['POST'])
async def webhook():
    token = os.getenv('BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()

    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)

    return 'ok'

if __name__ == '__main__':
    # Set up Flask app
    port = int(os.environ.get('PORT', 8443))
    
    # Set webhook URL
    bot_token = os.getenv('BOT_TOKEN')
    webhook_url = f'https://gachaidsaver.onrender.com/webhook'  # Replace with your actual Render URL
    
    bot = Bot(token=bot_token)
    bot.set_webhook(webhook_url)
    
    # Add command handlers
    application = ApplicationBuilder().token(bot_token).build()
    application.bot.set_webhook(webhook_url)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("myids", myids))
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port)
