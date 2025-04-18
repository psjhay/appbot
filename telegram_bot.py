import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests

TELEGRAM_API_TOKEN = '7630329200:AAGL585AzCfLJPZ8xC-CNxyzHxma1lLjgmo'  # Replace with your Bot Token
FASTAPI_URL = 'https://appsolutebot-production.up.railway.app'  # Replace with your FastAPI endpoint URL

async def start(update: Update, context):
    # Send a welcome message to the user when they start the conversation
    welcome_message = (
        "Welcome to AppSolute Bot! 😃\n\n"
        "I am here to assist you. Just type your query, and I'll do my best to help you!"
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context):
    user_message = update.message.text

    # Send the message to your FastAPI backend
    response = requests.post(FASTAPI_URL, json={"message": user_message})
    bot_response = response.json().get("response", "Sorry, I couldn't understand that.")

    # Send the response back to the user
    await update.message.reply_text(bot_response)

def main():
    # Create an Application object (new in v20.x)
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))  # Start command will trigger welcome
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
