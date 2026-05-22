import os
import shutil
from uuid import uuid4

from core.fluxo_conciliacao import executar_fluxo_conciliacao


PASTA_TEMP = "temp_uploads"
PASTA_SAIDA = "saida_testes"


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
    print("\n================ DEBUG WEB ================")
    print(f"Instituicao recebida: {instituicao}")
    print(f"Arquivo ERP recebido: {arquivo_erp.filename}")
    print(f"Arquivo instituicao recebido: {arquivo_instituicao.filename}")

    caminho_erp = salvar_upload(
        arquivo=arquivo_erp,
        prefixo="erp"
    )

    caminho_instituicao = salvar_upload(
        arquivo=arquivo_instituicao,
        prefixo=instituicao
    )

    print(f"Caminho ERP salvo: {caminho_erp}")
    print(f"Caminho instituicao salvo: {caminho_instituicao}")

    resultado = executar_fluxo_conciliacao(
        instituicao=instituicao,
        caminho_erp=caminho_erp,
        caminho_instituicao=caminho_instituicao,
        pasta_saida=PASTA_SAIDA,
        salvar_intermediarios=True,
    )

    print("\n================ RESULTADO WEB ================")

    print("ERP padronizado:")
    print(resultado["df_erp_padronizado"].shape)

    print("Instituicao padronizada:")
    print(resultado["df_instituicao_padronizado"].shape)

    print("Conciliação:")
    print(resultado["df_conciliado"]["status_conciliacao"].value_counts(dropna=False))

    print("Relatório:")
    print(resultado["relatorio"])

    print("Download:")
    print(resultado["download"])

    return resultado