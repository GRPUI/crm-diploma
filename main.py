import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from deps import DatabaseMarker, SettingsMarker
from core.db import DatabaseHandler
import dotenv
import os

from settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.dependency_overrides[SettingsMarker]()
    db = DatabaseHandler(
        url=f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )

    app.dependency_overrides.update({DatabaseMarker: lambda: db})
    await db.init()

    yield

    await db.close_connection()


def register_app(settings: Settings) -> FastAPI:
    app = FastAPI(lifespan=lifespan, redoc_url=None)
    app.include_router(router)

    app.dependency_overrides.update({SettingsMarker: lambda: settings})

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
    )

    return app


dotenv.load_dotenv()

settings = Settings(
    db_name=os.getenv("DB_NAME", "tg_tinder"),
    db_host=os.getenv("DB_HOST", "150.241.99.152"),
    db_port=int(os.getenv("DB_PORT", "2260")),
    db_user=os.getenv("DB_USER", "kramer"),
    db_password=os.getenv("DB_PASSWORD", "dmIiMBrMQQa5r2xAzm65o2OwR"),
    cors_allowed_origins=["*"],
    cors_allowed_methods=["*"],
    cors_allowed_headers=["*"],
    jwt_secret_key=os.getenv(
        "JWT_SECRET", "VSJntWUYE_Gw(L;M[=$cDbdrC`p,>8a4Q^e.Hx}9jq&?*g+sKy"
    ),
    is_prod=os.getenv("IS_PROD", True),
)

app = register_app(settings=settings)


if __name__ == "__main__":
    config = uvicorn.Config(app, host="127.0.0.1", port=8015, workers=4)

    server = uvicorn.Server(config)

    asyncio.run(server.serve())
