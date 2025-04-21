from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS (можно ограничить конкретными origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Модель запроса
class StyleRequest(BaseModel):
    text: str
    style: str  # например: "formal", "conversational"
    language: str = "ru"

# Модель ответа
class StyleResponse(BaseModel):
    original_text: str
    transformed_text: str
    style: str

# Prompt, адаптируемый по стилю и языку
def build_prompt(text: str, style: str, language: str) -> str:
    instructions = {
        "formal": {
            "ru": "Перепиши текст в формальном деловом стиле.",
            "en": "Rewrite the text in a formal business tone."
        },
        "conversational": {
            "ru": "Сделай текст более разговорным и неформальным.",
            "en": "Make the text more conversational and informal."
        },
        "literary": {
            "ru": "Преобразуй текст в художественный, с образными выражениями.",
            "en": "Transform the text into a literary, expressive style."
        },
        "simple": {
            "ru": "Сделай текст проще и понятнее.",
            "en": "Simplify the text for clarity and accessibility."
        },
        "emotional-positive": {
            "ru": "Добавь позитивный эмоциональный окрас.",
            "en": "Add a positive emotional tone."
        },
        "emotional-negative": {
            "ru": "Добавь негативный эмоциональный окрас.",
            "en": "Add a negative emotional tone."
        },
    }

    instruction = instructions.get(style, {}).get(language)
    if not instruction:
        raise ValueError("Unsupported style or language.")

    return f"{instruction}\n\nТекст:\n{text}"

@app.post("/style", response_model=StyleResponse)
async def style_text(request: StyleRequest):
    try:
        prompt = build_prompt(request.text, request.style, request.language)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник по стилистике текста."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        transformed = response.choices[0].message.content.strip()

        return StyleResponse(
            original_text=request.text,
            transformed_text=transformed,
            style=request.style
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
