from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.conciliacao_routes import router as conciliacao_router


app = FastAPI(
    title="Conciliador Modular",
    description="API para conciliação entre ERP e instituições financeiras.",
    version="1.0.0",
)


@app.get("/api/status")
def health_check():
    return {
        "status": "online",
        "mensagem": "API do Conciliador Modular funcionando."
    }


app.include_router(
    conciliacao_router,
    prefix="/conciliacao",
    tags=["Conciliação"]
)


app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)