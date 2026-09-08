import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("data/knowledge_base.json", "r") as f:
    KNOWLEDGE_BASE = json.load(f)

STANDARDS = KNOWLEDGE_BASE.get("indian_standards", [])
QA_PAIRS = KNOWLEDGE_BASE.get("consumer_faqs", [])


class Question(BaseModel):
    question: str


def retrieve_context(question: str, top_n: int = 3):
    q_words = set(question.lower().split())
    scored = []

    for item in QA_PAIRS:
        text = (item.get("question", "") + " " + item.get("answer", "")).lower()
        score = sum(1 for w in q_words if w in text)
        if score > 0:
            scored.append((score, "qa", item))

    for item in STANDARDS:
        text = (item.get("title", "") + " " + item.get("description", "") + " " + item.get("category", "")).lower()
        score = sum(1 for w in q_words if w in text)
        if score > 0:
            scored.append((score, "standard", item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_n]


def format_context(matches):
    lines = []
    for score, kind, item in matches:
        if kind == "qa":
            lines.append(f"Q: {item.get('question')}\nA: {item.get('answer')}\nSource: {item.get('is_number', item.get('category', 'BIS FAQ'))}")
        else:
            lines.append(f"Standard {item.get('is_number')}: {item.get('title')}\nDescription: {item.get('description')}\nSource: {item.get('document_url')}")
    return "\n\n".join(lines)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: Question):
    matches = retrieve_context(payload.question)

    if not matches:
        return {
            "answer": "I don't have information on that in my current knowledge base. Please check bis.gov.in directly.",
            "sources": []
        }

    context = format_context(matches)

    prompt = f"""You are a BIS (Bureau of Indian Standards) assistant. Using ONLY the context below, answer the question clearly and concisely. Always mention the relevant standard number or source if available. If the context doesn't fully answer the question, say so honestly.

Context:
{context}

Question: {payload.question}

Answer:"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    sources = [item.get("is_number") or item.get("category") for _, _, item in matches]

    return {
        "answer": response.text,
        "sources": sources
    }