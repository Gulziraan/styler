# Telegram Text Styler Backend

## Как запустить

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Создай `.env` файл на основе `.env.example` и вставь туда свой OpenAI API ключ.

3. Запусти сервер:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Эндпоинт

POST `/style`

Тело запроса:
```json
{
  "text": "Твой текст",
  "style": "научный"
}
```

Ответ:
```json
{
  "result": "Преобразованный текст"
}
```