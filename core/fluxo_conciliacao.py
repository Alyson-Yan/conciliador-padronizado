import os

from modulo_1_selecao.instituicoes import (
    obter_padronizador_instituicao,
    obter_conciliador_instituicao,
)

from modulo_2_upload.leitor_arquivos import (
    carregar_arquivo_erp,
    carregar_arquivo_instituicao,
)

from modulo_3_padronizacao.erp_padronizador import padronizar_erp
from modulo_5_relatorio.gerar_relatorio import gerar_relatorio_conciliacao
from modulo_6_download.preparar_download import preparar_arquivo_download
from core.validacao_fluxo import validar_resultado_fluxo

def montar_caminhos_saida(instituicao, pasta_saida):
    pasta_download = os.path.join(pasta_saida, "download")

    return {
        "pasta_saida": pasta_saida,
        "pasta_download": pasta_download,
        "erp_padronizado": os.path.join(
            pasta_saida,
            "erp_padronizado.xlsx"
        ),
        "instituicao_padronizada": os.path.join(
            pasta_saida,
            f"{instituicao}_padronizada.xlsx"
        ),
        "conciliacao_teste": os.path.join(
            pasta_saida,
            f"{instituicao}_conciliada_teste.xlsx"
        ),
        "relatorio": os.path.join(
            pasta_saida,
            f"relatorio_conciliacao_{instituicao}.xlsx"
        ),
    }


def salvar_excel(df, caminho_saida):
    df.to_excel(caminho_saida, index=False)


def executar_fluxo_conciliacao(
    instituicao,
    caminho_erp,
    caminho_instituicao,
    pasta_saida,
    salvar_intermediarios=True,
):
    instituicao = instituicao.lower().strip()

    os.makedirs(pasta_saida, exist_ok=True)

    caminhos = montar_caminhos_saida(
        instituicao=instituicao,
        pasta_saida=pasta_saida
    )

    os.makedirs(caminhos["pasta_download"], exist_ok=True)

    padronizador_instituicao = obter_padronizador_instituicao(instituicao)
    conciliador = obter_conciliador_instituicao(instituicao)

    # =========================
    # 1. Leitura dos arquivos
    # =========================

    df_erp_bruto = carregar_arquivo_erp(caminho_erp)

    df_instituicao_bruto = carregar_arquivo_instituicao(
        caminho_arquivo=caminho_instituicao,
        instituicao=instituicao
    )

    # =========================
    # 2. Padronização
    # =========================

    df_erp_padronizado = padronizar_erp(df_erp_bruto)

    df_instituicao_padronizado = padronizador_instituicao(
        df_instituicao_bruto
    )

    if salvar_intermediarios:
        salvar_excel(
            df_erp_padronizado,
            caminhos["erp_padronizado"]
        )

        salvar_excel(
            df_instituicao_padronizado,
            caminhos["instituicao_padronizada"]
        )

    # =========================
    # 3. Conciliação
    # =========================

    df_conciliado, df_erp_resultado = conciliador(
        df_instituicao_padronizado,
        df_erp_padronizado
    )

    if salvar_intermediarios:
        salvar_excel(
            df_conciliado,
            caminhos["conciliacao_teste"]
        )

    # =========================
    # 4. Relatório
    # =========================

    resultado_relatorio = gerar_relatorio_conciliacao(
        df_conciliado=df_conciliado,
        caminho_saida=caminhos["relatorio"],
        instituicao=instituicao,
    )

    # =========================
    # 5. Download
    # =========================

    resultado_download = preparar_arquivo_download(
        caminho_relatorio_origem=resultado_relatorio["caminho_saida"],
        pasta_saida=caminhos["pasta_download"],
        instituicao=instituicao,
        df_conciliado=df_conciliado,
    )

    resultado = {
        "instituicao": instituicao,
        "caminhos": caminhos,
        "df_erp_padronizado": df_erp_padronizado,
        "df_instituicao_padronizado": df_instituicao_padronizado,
        "df_conciliado": df_conciliado,
        "df_erp_resultado": df_erp_resultado,
        "relatorio": resultado_relatorio,
        "download": resultado_download,
    }

    resultado["validacao"] = validar_resultado_fluxo(resultado)

    return resultado