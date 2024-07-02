from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to store user IDs and their game IDs
user_data = {}

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

app = Flask(__name__)

@app.route('/<token>', methods=['POST'])
async def webhook(token):
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("myids", myids))

    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)

    return 'ok'

if __name__ == '__main__':
    token = os.getenv('BOT_TOKEN')
    port = int(os.environ.get('PORT', 8443))
    url = f"https://your_render_url/{token}"

    # Set webhook
    application = ApplicationBuilder().token(token).build()
    application.bot.set_webhook(url)

    app.run(host='0.0.0.0', port=port)
