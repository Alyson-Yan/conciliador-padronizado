import os
import pandas as pd

from modulo_1_selecao.instituicoes import obter_formatos_aceitos


def obter_extensao(caminho_arquivo):
    return os.path.splitext(caminho_arquivo)[1].replace(".", "").lower()


def ler_arquivo_csv(caminho_arquivo, sep=";", encoding="latin1", header="infer"):
    return pd.read_csv(
        caminho_arquivo,
        sep=sep,
        encoding=encoding,
        header=header,
        low_memory=False
    )


def ler_arquivo_excel(caminho_arquivo, sheet_name=0, header=0):
    return pd.read_excel(
        caminho_arquivo,
        sheet_name=sheet_name,
        header=header
    )


def carregar_arquivo_erp(caminho_arquivo):
    extensao = obter_extensao(caminho_arquivo)

    if extensao != "csv":
        raise ValueError(
            f"Formato .{extensao} não aceito para ERP. O ERP deve ser .csv."
        )

    return ler_arquivo_csv(
        caminho_arquivo,
        sep=";",
        encoding="latin1"
    )


def carregar_arquivo_instituicao(caminho_arquivo, instituicao):
    instituicao = instituicao.lower().strip()

    formatos_aceitos = obter_formatos_aceitos(instituicao)
    extensao = obter_extensao(caminho_arquivo)

    if extensao not in formatos_aceitos:
        raise ValueError(
            f"Formato .{extensao} não aceito para {instituicao}. "
            f"Formatos aceitos: {formatos_aceitos}"
        )

    if extensao == "csv":
        if instituicao == "credishop":
            return ler_arquivo_csv(
                caminho_arquivo,
                sep=";",
                encoding="latin1",
                header=None
            )

        if instituicao == "pagbank":
            return ler_arquivo_csv(
                caminho_arquivo,
                sep=";",
                encoding="utf-8-sig"
            )

        return ler_arquivo_csv(
            caminho_arquivo,
            sep=";",
            encoding="latin1"
        )

    if extensao in ["xlsx", "xls"]:
        if instituicao == "santander":
            print("DEBUG: lendo Santander com sheet_name='Detalhado' e header=None")

            return ler_arquivo_excel(
                caminho_arquivo,
                sheet_name="Detalhado",
                header=None
            )

        return ler_arquivo_excel(
            caminho_arquivo
        )

    raise ValueError(f"Formato não suportado: {extensao}")