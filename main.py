from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import g4f

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    character: str
    userName: str
    userGender: str


@app.post("/")
async def chat(req: ChatRequest):

    prompt = f"""
Ты персонаж {req.character}.
Пользователь: {req.userName}.
Пол пользователя: {req.userGender}.

Сообщение пользователя:
{req.message}

Отвечай как {req.character}.
"""

    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return {"reply": response}

    except Exception as e:
        return {"reply": f"Ошибка ИИ: {str(e)}"}
