from fastapi import FastAPI

from app.routes.conciliacao_routes import router as conciliacao_router


app = FastAPI(
    title="Conciliador Modular",
    description="API para conciliação entre ERP e instituições financeiras.",
    version="1.0.0",
)


@app.get("/")
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