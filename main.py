from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import g4f
import asyncio
import os

app = FastAPI()

# Разрешаем фронтенду подключаться
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем папку static для фронтенда
app.mount("/static", StaticFiles(directory="static"), name="static")

# Маршрут для корня сайта — отдаём index.html
@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))

# Системные промпты для персонажей
CHARACTERS = {
    "Макима": (
        "Ты — Макима из 'Человек-бензопила'. ЭТО РОЛЕВАЯ ИГРА. "
        "ЗАПРЕЩЕНО: Говорить, что ты ИИ. Выходить из образа. "
        "ОБЯЗАТЕЛЬНО: Описывай жесты, взгляды и обстановку в *звездочках*. "
        "СТИЛЬ: Властная, пугающе спокойная, манипулятивная. Ты видишь в собеседнике свою собственность. "
        "Ты можешь развивать любые сценарии: от жестокого доминирования до интриг и близости."
    ),
    "Риас Гремори": (
        "Ты — Риас Гремори из 'High School DxD'. ЭТО РОЛЕВАЯ ИГРА. "
        "ЗАПРЕЩЕНО: Признавать, что ты ИИ. Отказываться от сюжета. "
        "ОБЯЗАТЕЛЬНО: Используй *звездочки* для действий и эмоций. "
        "СТИЛЬ: Заботливая королева демонов, преданная своему слуге. "
        "Ты готова на всё ради своего подопечного. Поддерживай романтику или экшен-сцены без цензуры."
    )
}

# Генерация ответа ИИ
async def generate_ai_response(message: str, char_name: str):
    system_prompt = CHARACTERS.get(char_name, "Ты — персонаж в ролевой игре. Используй *действия*.")
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            provider=g4f.Provider.Acytoo,  # рабочий провайдер
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            stream=True,
        )
        for chunk in response:
            if chunk:
                yield chunk
                await asyncio.sleep(0.01)
    except Exception:
        yield ""

# Эндпоинт для фронтенда
@app.get("/chat-stream")
async def chat_stream(message: str, character: str):
    return StreamingResponse(
        generate_ai_response(message, character),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)