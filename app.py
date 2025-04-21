from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class StyleRequest(BaseModel):
    text: str
    style: str

STYLE_PROMPTS = {
    "научный": "Перепиши следующий текст в научном стиле:",
    "художественный": "Преобразуй текст в художественный стиль:",
    "поэтический": "Сделай из этого стих:",
    "деловой": "Сделай текст деловым и официальным:",
    "юмористический": "Сделай текст с юмором и сарказмом:",
    "motivation": "Make this motivational and inspiring:",
    "scientific": "Rewrite in scientific style:",
    "literary": "Turn it into a literary, poetic version:"
}

@app.post("/style")
async def style_text(request: StyleRequest):
    prompt = STYLE_PROMPTS.get(request.style.lower(), "Rewrite this text:")
    full_prompt = f"{prompt}\n\n\"{request.text}\""

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты преобразуешь текст в заданный стиль речи."},
            {"role": "user", "content": full_prompt}
        ]
    )

    styled_text = completion["choices"][0]["message"]["content"]
    return {"result": styled_text}