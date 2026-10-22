import os
import json
import sqlite3
import traceback
import chromadb
from google import genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. Initialize core server architecture framework
app = FastAPI()

# Initialize Google GenAI client (Securely grabs GEMINI_API_KEY from system environments)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Persistent ChromaDB client saves vector embeddings locally in the './chroma_db' folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="first_db")


# 2. Relational Database (SQLite) Configuration Layer
def init_sql_db():
    """Spins up a local SQLite file to permanently hold relational chat logs."""
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT,
            ai_answer TEXT
        )
    """)
    conn.commit()
    conn.close()

# Execute database structure initialization table creation routines immediately on start
init_sql_db()


# 3. Pydantic Models for Input Validation
class doc_input(BaseModel):
    docs_id: str
    text: str

class query(BaseModel):
    prompt: str


# 4. Endpoint 1: Upload and vector index documents
@app.post("/add_docs")
async def add_doc(data: doc_input):
    try:
        # Wrap parameters within standard Python Lists []
        collection.add(
            documents=[data.text], 
            ids=[data.docs_id]
        )
        return {
            "status": "success",
            "message": f"Document '{data.docs_id}' successfully stored in ChromaDB vector files!",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 5. Endpoint 2: Grounded RAG Query Operations
@app.post("/query")
async def query_func(data: query):
    try:
        # Math similarity lookups: Retrieve the top 1 single closest matching block
        result = collection.query(
            query_texts=[data.prompt], 
            n_results=1
        )

        # Handle structural validation check scenarios where vector storage indexes are empty
        if not result["documents"] or not result["documents"][0]:
            return {
                "ai_answer": "The vector database is currently completely empty. Please ingest your source files first."
            }

        # Dig down step-by-step using list index matrices to extract raw string text context
        retrieved_context = result["documents"][0][0]

        # Pack instructions, vector data inputs, and prompt variables into a single unified packet string
        prompt_content = f"""You are an AI assistant and must answer according to the context given with respect to the user question.

Context: {retrieved_context}
Question: {data.prompt}
"""

        # Fire unified text payload request over network via Google SDK parameters
        response = client.models.generate_content(
            model="gemini-3.8-flash", 
            contents=prompt_content
        )

        # Defensive Execution Parsing: Extract response string or safely catch safety blocks using getattr
        answer_text = getattr(response, "text", None)
        if not answer_text:
            answer_text = "I couldn't generate a clear response based on the context provided."

        # 📊 RELATIONAL LOGGING LAYER: Save interaction context data straight to SQLite database file
        conn = sqlite3.connect("chat_history.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_question, ai_answer) VALUES (?, ?)",
            (data.prompt, answer_text)
        )
        conn.commit()
        conn.close()
        print("📊 Relational Database: History record logged successfully into SQLite!")

        return {"ai_answer": answer_text}
        
    except Exception as e:
        # Generate full stack execution error trails directly to trace network bugs fast
        error_detail = traceback.format_exc()
        print("--- TRACEBACK ERROR LOG ---")
        print(error_detail)
        print("---------------------------")
        raise HTTPException(status_code=500, detail=str(e))


# 6. Endpoint 3: History log extraction endpoint
@app.get("/history")
async def get_chat_history():
    try:
        conn = sqlite3.connect("chat_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_question, ai_answer FROM chat_logs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # Turn standard database row outputs cleanly into arrays of Python dictionary schemas
        history_list = [{"user": row[0], "ai": row[1]} for row in rows]
        return {"history": history_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
