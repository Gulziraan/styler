from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "YOUR_GROQ_API_KEY"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

STYLE_PROMPTS = {
    "formal": "Сделай текст формальным, сохрани язык и смысл, не добавляй ничего лишнего.",
    "literary": "Переделай текст в художественном стиле, используя метафоры и выразительность.",
    "conversational": "Сделай текст разговорным, как будто говоришь с другом.",
    "simple": "Упростить текст, чтобы он был понятен даже ребенку.",
    "emotional-positive": "Сделай текст позитивным и вдохновляющим, сохрани смысл.",
    "emotional-negative": "Сделай текст драматичным и с оттенком печали, сохрани смысл."
}

@app.post("/style")
async def style_text(request: Request):
    data = await request.json()
    original_text = data.get("text")
    selected_style = data.get("style")

    if not original_text or not selected_style:
        return {"error": "Both 'text' and 'style' must be provided"}

    style_instruction = STYLE_PROMPTS.get(selected_style)
    if not style_instruction:
        return {"error": f"Style '{selected_style}' is not supported."}

    prompt = f"{style_instruction} Вот текст: {original_text}"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Ты ассистент, который переформулирует текст на русском языке в стиле: {style}. Если текст не на русском — сначала переведи его на русский, а затем переформулируй. Никогда не используй английский язык в ответе. Переформулируй следующий текст:"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        result = response.json()

    try:
        content = result['choices'][0]['message']['content']
        return {"styled_text": content}
    except Exception:
        return {"error": "Failed to get response", "details": result}
