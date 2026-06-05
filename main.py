import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_KEY = os.environ.get('GOOGLE_API_KEY')
CX = os.environ.get('SEARCH_ENGINE_ID')

async def search(update, context):
    query = " ".join(context.args)
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}"
    response = requests.get(url).json()
    if 'items' in response:
        await update.message.reply_text(f"{response['items'][0]['title']}\n{response['items'][0]['link']}")
    else:
        await update.message.reply_text("没找到结果")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("search", search))
    app.run_polling()
