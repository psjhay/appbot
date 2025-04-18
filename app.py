# app.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
import os

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

