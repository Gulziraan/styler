from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import openai
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class StyleRequest(BaseModel):
    text: str
    style: str
    language: str = "ru"

# Response schema
class StyleResponse(BaseModel):
    originalText: str
    transformedText: str
    style: str

# Style prompt templates
STYLE_PROMPTS = {
    "formal": {
        "ru": "Перепиши следующий текст в деловом, официальном стиле:\n\n{input}",
        "en": "Rewrite the following text in a formal, business tone:\n\n{input}",
    },
    "conversational": {
        "ru": "Сделай этот текст неформальным и разговорным:\n\n{input}",
        "en": "Make this text informal and conversational:\n\n{input}",
    },
    "literary": {
        "ru": "Преврати этот текст в художественный рассказ:\n\n{input}",
        "en": "Transform this text into a literary passage:\n\n{input}",
    },
    "simple": {
        "ru": "Упрости следующий текст, сохранив смысл:\n\n{input}",
        "en": "Simplify the following text while keeping its meaning:\n\n{input}",
    },
    "emotional-positive": {
        "ru": "Сделай текст эмоциональным и с позитивным настроем:\n\n{input}",
        "en": "Make this text emotional with a positive tone:\n\n{input}",
    },
    "emotional-negative": {
        "ru": "Передай в тексте сильные отрицательные эмоции:\n\n{input}",
        "en": "Make this text emotional with a negative tone:\n\n{input}",
    },
}

@app.post("/style", response_model=StyleResponse)
async def style_text(request: StyleRequest):
    prompt_template = STYLE_PROMPTS.get(request.style, {}).get(request.language)
    if not prompt_template:
        raise HTTPException(status_code=400, detail="Unsupported style or language")

    prompt = prompt_template.format(input=request.text)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник, преобразующий текст в заданный стиль."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        transformed_text = response.choices[0].message.content.strip()
        return StyleResponse(
            originalText=request.text,
            transformedText=transformed_text,
            style=request.style,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
