import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import httpx  # For async requests

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

# Set up the Telegram bot using Application from telegram.ext
TELEGRAM_API_TOKEN = '7630329200:AAGL585AzCfLJPZ8xC-CNxyzHxma1lLjgmo'
WEBHOOK_URL = "https://appsolutebot-production.up.railway.app/webhook"  # Replace with your actual webhook URL

# Initialize the Telegram bot application
bot_app = Application.builder().token(TELEGRAM_API_TOKEN).build()

# Start command handler for Telegram Bot
async def start(update: Update, context):
    welcome_message = (
        "Welcome to AppSolute Bot! 😃\n\n"
        "I am here to assist you. Just type your query, and I'll do my best to help you!"
    )
    await update.message.reply_text(welcome_message)

# Message handler for Telegram Bot
async def handle_message(update: Update, context):
    user_message = update.message.text

    # Send the message to your FastAPI backend (chat endpoint)
    async with httpx.AsyncClient() as client:
        response = await client.post("https://appsolutebot-production.up.railway.app/chat", json={"message": user_message})
        bot_response = response.json().get("response", "Sorry, I couldn't understand that.")
    
    # Send the response back to the user on Telegram
    await update.message.reply_text(bot_response)

# Webhook handler for FastAPI (receives updates from Telegram)
@app.post("/webhook")
async def webhook_handler(request: Request):
    update = await request.json()
    print("Received update:", update)
    
    # Forward the update to the bot's dispatcher
    dispatcher = bot_app.updater.dispatcher
    update_obj = Update.de_json(update, bot_app.bot)
    dispatcher.process_update(update_obj)

    return {"status": "ok"}

# FastAPI event to set the webhook on startup
@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    print("Webhook is set successfully.")
