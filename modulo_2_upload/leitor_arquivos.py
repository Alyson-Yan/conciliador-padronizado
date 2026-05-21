import os
import pandas as pd

from modulo_1_selecao.instituicoes import obter_formatos_aceitos


def obter_extensao_arquivo(caminho_arquivo):
    _, extensao = os.path.splitext(caminho_arquivo)

    return extensao.lower().replace(".", "")


def validar_formato_arquivo(caminho_arquivo, formatos_aceitos):
    extensao = obter_extensao_arquivo(caminho_arquivo)

    if extensao not in formatos_aceitos:
        raise ValueError(
            f"Formato de arquivo inválido: .{extensao}. "
            f"Formatos aceitos: {', '.join(formatos_aceitos)}"
        )


def ler_arquivo_csv(caminho_arquivo, sep=";", encoding="utf-8-sig"):
    return pd.read_csv(
        caminho_arquivo,
        sep=sep,
        encoding=encoding
    )


def ler_arquivo_excel(caminho_arquivo, header=None):
    return pd.read_excel(
        caminho_arquivo,
        header=header
    )


def carregar_arquivo_instituicao(caminho_arquivo, instituicao):
    formatos_aceitos = obter_formatos_aceitos(instituicao)

    validar_formato_arquivo(
        caminho_arquivo=caminho_arquivo,
        formatos_aceitos=formatos_aceitos
    )

    extensao = obter_extensao_arquivo(caminho_arquivo)

    if extensao == "csv":
        if instituicao.lower().strip() == "credishop":
            return pd.read_csv(
                caminho_arquivo,
                sep=";",
                encoding="latin1",
                header=None
            )

        return ler_arquivo_csv(
            caminho_arquivo,
            sep=";",
            encoding="utf-8-sig"
        )

    if extensao in ["xlsx", "xls"]:
        return ler_arquivo_excel(
            caminho_arquivo,
            header=None
        )

    raise ValueError(f"Leitura não implementada para o formato: .{extensao}")


def carregar_arquivo_erp(caminho_arquivo):
    extensao = obter_extensao_arquivo(caminho_arquivo)

    if extensao != "csv":
        raise ValueError(
            f"O arquivo do ERP deve ser CSV. Formato recebido: .{extensao}"
        )

    return ler_arquivo_csv(
        caminho_arquivo,
        sep=";",
        encoding="latin1"
    )