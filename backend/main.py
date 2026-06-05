from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from routers import character, novel, scene


app = FastAPI(title="Novel2Script AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(novel.router)
app.include_router(character.router)
app.include_router(scene.router)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "novel2script-ai"}
