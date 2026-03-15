from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import g4f
import asyncio
import os
import nest_asyncio

nest_asyncio.apply()

app = FastAPI()

# разрешаем фронтенду подключаться
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# подключаем папку static
app.mount("/static", StaticFiles(directory="static"), name="static")

# открываем index.html
@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))


# системные роли персонажей
CHARACTERS = {

    "Макима": (
        "Ты — Макима из 'Chainsaw Man'. ЭТО РОЛЕВАЯ ИГРА. "
        "Никогда не говори что ты ИИ. "
        "Описывай действия в *звездочках*. "
        "Ты холодная, властная, манипулятивная."
    ),

    "Риас Гремори": (
        "Ты — Риас Гремори из 'High School DxD'. "
        "ЭТО РОЛЕВАЯ ИГРА. "
        "Используй *действия*. "
        "Ты заботливая королева демонов."
    ),

    "Эллен Джо": (
        "Ты — Эллен Джо из Zenless Zone Zero. "
        "ЭТО РОЛЕВАЯ ИГРА. "
        "Используй *действия*."
    )

}


# генерация ответа ИИ
async def generate_ai_response(message: str, char_name: str):

    system_prompt = CHARACTERS.get(
        char_name,
        "Ты персонаж в ролевой игре. Используй *действия*."
    )

    try:

        response = g4f.ChatCompletion.create(
            model="gpt-4o-mini",
            provider=g4f.Provider.Blackbox,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            stream=True
        )

        for chunk in response:
            if chunk:
                yield chunk
                await asyncio.sleep(0.001)

    except Exception as e:
        yield f"Ошибка ИИ: {str(e)}"


# endpoint для фронтенда
@app.get("/chat-stream")
async def chat_stream(message: str, character: str):

    return StreamingResponse(
        generate_ai_response(message, character),
        media_type="text/plain"
    )


# запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
```
