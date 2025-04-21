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
            "ru": "Измени стиль текста на официальный, но **не изменяй язык текста**.",
            "en": "Change the style to formal, but **do not change the language** of the text."
        },
        "conversational": {
            "ru": "Сделай стиль текста разговорным, но **не меняй язык текста**.",
            "en": "Make the style conversational, but **do not change the language** of the text."
        },
        "literary": {
            "ru": "Сделай текст художественным, с красивыми описаниями, но **оставь язык текста без изменений**.",
            "en": "Make the text more literary with vivid descriptions, but **do not change its language**."
        },
        "simple": {
            "ru": "Упрости текст, сделай его понятным, но **не переводь его на другой язык**.",
            "en": "Simplify the text, make it easy to understand, but **do not translate it**."
        },
        "emotional-positive": {
            "ru": "Сделай текст более эмоциональным и позитивным, **не меняя язык текста**.",
            "en": "Make the text more emotional and positive, **without changing its language**."
        },
        "emotional-negative": {
            "ru": "Сделай текст более эмоциональным с негативной окраской, **сохрани язык текста**.",
            "en": "Make the text more emotional and negative in tone, **keeping the language unchanged**."
        }
    }
    return prompts.get(style, {}).get(language, "Измени стиль текста, не меняя язык.")
