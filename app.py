from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# CORS (на время разработки можно разрешить все источники)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Новый клиент OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class StyleRequest(BaseModel):
    text: str
    style: str

@app.post("/style")
async def style_text(request: StyleRequest):
    try:
        messages = [
            {"role": "system", "content": f"Преобразуй стиль текста в стиль: {request.style}"},
            {"role": "user", "content": request.text}
        ]

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        transformed = completion.choices[0].message.content
        return {
            "original": request.text,
            "transformed": transformed.strip(),
            "style": request.style
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
