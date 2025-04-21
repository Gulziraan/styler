# app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Установи переменную в Railway
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

class StyleRequest(BaseModel):
    text: str
    style: str
    language: str = "ru"

@app.post("/style")
async def style_text(req: StyleRequest):
    system_message = get_prompt(req.style, req.language)
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": req.text}
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text
        }

    data = response.json()
    result = data["choices"][0]["message"]["content"]
    return {"transformedText": result}

def get_prompt(style: str, language: str) -> str:
    prompts = {
        "formal": {
            "ru": "Преобразуй текст в деловой официальный стиль.",
            "en": "Transform the text into a formal business tone."
        },
        "conversational": {
            "ru": "Преобразуй текст в простой разговорный стиль.",
            "en": "Make the text sound casual and conversational."
        },
        "literary": {
            "ru": "Сделай текст более художественным, с красивыми описаниями.",
            "en": "Enhance the text with literary and artistic language."
        },
        "simple": {
            "ru": "Сделай текст простым и понятным.",
            "en": "Make the text very simple and easy to understand."
        },
        "emotional-positive": {
            "ru": "Сделай текст эмоциональным с позитивной окраской.",
            "en": "Make the text emotional and positive."
        },
        "emotional-negative": {
            "ru": "Сделай текст эмоциональным с негативной окраской.",
            "en": "Make the text emotional and negative."
        }
    }
    return prompts.get(style, {}).get(language, "Перепиши текст.")
