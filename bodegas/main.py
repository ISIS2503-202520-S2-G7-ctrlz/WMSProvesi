import uvicorn
from fastapi import FastAPI
import views
from models.db import set_bodegas_db


def create_app():
    app = FastAPI(
        docs_url="/bodegas/docs",
        openapi_url="/bodegas/openapi.json",
        redoc_url=None,
    )

    @app.on_event("startup")
    async def on_startup():
        await set_bodegas_db()

    app.include_router(views.router)

    return app

app = create_app()
if __name__ == "__main__":
    # avoid redirects
    uvicorn.run(app, host="0.0.0.0", port=8080)