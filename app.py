from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
import os
from telegram import Update
from telegram.ext import Application
import json
import requests

# Load your Google API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBN9HaY_wtVkx9P0KOAovL7LNyM8k7Cq3Q"

# Configure Gemini + LlamaIndex
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

embedding_model = GeminiEmbedding(model_name="embedding-001")
llm = Gemini(model="gemini-2.0-flash")

Settings.llm = llm
Settings.embed_model = embedding_model

# Load documents (e.g., PDFs, FAQs)
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(similarity_top_k=3)

# FastAPI app
app = FastAPI()

# Define the Telegram Bot Token
TELEGRAM_API_TOKEN = '7630329200:AAGL585AzCfLJPZ8xC-CNxyzHxma1lLjgmo'

# Set up the Telegram bot application
application = Application.builder().token(TELEGRAM_API_TOKEN).build()

# Define start command for Telegram Bot
async def start(update: Update, context):
    welcome_message = (
        "Welcome to AppSolute Bot! 😃\n\n"
        "I am here to assist you. Just type your query, and I'll do my best to help you!"
    )
    await update.message.reply_text(welcome_message)

# Define handler for text messages
async def handle_message(update: Update, context):
    user_message = update.message.text

    # Send the message to your FastAPI backend or another service
    response = requests.post("https://your-backend-url", json={"message": user_message})
    bot_response = response.json().get("response", "Sorry, I couldn't understand that.")

    # Send the response back to the user
    await update.message.reply_text(bot_response)

# Add handlers to your bot application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook route to receive Telegram updates
@app.post("/webhook")
async def webhook_handler(request: Request):
    # Get the incoming update from Telegram
    update = await request.json()
    print("Received update:", update)

    # Process the update and forward it to the Telegram bot
    application.update_queue.put(Update.de_json(update, application.bot))

    # Return a response to Telegram (200 status code is expected by Telegram)
    return {"status": "ok"}

# Chat endpoint for handling user requests
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    query = request.message
    response = query_engine.query(query)
    return {"response": str(response)}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>🤖 Welcome to AppSolute Bot!</h2>
    <p>This bot is live and ready to help you! 🚀</p>
    <p>Send a POST request to <code>/chat</code> with a message to start chatting.</p>
    """
