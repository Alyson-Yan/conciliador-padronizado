import os
import shutil
from uuid import uuid4

from core.fluxo_conciliacao import executar_fluxo_conciliacao


PASTA_TEMP = "temp_uploads"
PASTA_SAIDA = "saida"

def garantir_pastas():
    os.makedirs(PASTA_TEMP, exist_ok=True)
    os.makedirs(PASTA_SAIDA, exist_ok=True)


def salvar_upload(arquivo, prefixo):
    garantir_pastas()

    nome_seguro = arquivo.filename.replace(" ", "_")
    nome_final = f"{prefixo}_{uuid4().hex}_{nome_seguro}"

    caminho_destino = os.path.join(PASTA_TEMP, nome_final)

    with open(caminho_destino, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    return caminho_destino


def executar_conciliacao_web(instituicao, arquivo_erp, arquivo_instituicao):

    caminho_erp = salvar_upload(
        arquivo=arquivo_erp,
        prefixo="erp"
    )

    caminho_instituicao = salvar_upload(
        arquivo=arquivo_instituicao,
        prefixo=instituicao
    )


    resultado = executar_fluxo_conciliacao(
        instituicao=instituicao,
        caminho_erp=caminho_erp,
        caminho_instituicao=caminho_instituicao,
        pasta_saida=PASTA_SAIDA,
        salvar_intermediarios=False,
    )

    return resultado