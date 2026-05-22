from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.services.conciliacao_service import executar_conciliacao_web


router = APIRouter()


@router.post("/executar")
def executar_conciliacao(
    instituicao: str = Form(...),
    arquivo_erp: UploadFile = File(...),
    arquivo_instituicao: UploadFile = File(...),
):
    resultado = executar_conciliacao_web(
        instituicao=instituicao,
        arquivo_erp=arquivo_erp,
        arquivo_instituicao=arquivo_instituicao,
    )

    caminho_download = resultado["download"]["caminho_arquivo"]
    nome_arquivo = resultado["download"]["nome_arquivo"]

    return FileResponse(
        path=caminho_download,
        filename=nome_arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )