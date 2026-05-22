import os
import sys

CAMINHO_RAIZ = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if CAMINHO_RAIZ not in sys.path:
    sys.path.insert(0, CAMINHO_RAIZ)

from core.fluxo_conciliacao import executar_fluxo_conciliacao


# ============================================================
# CONFIGURAÇÕES DO TESTE
# ============================================================
# Aqui você escolhe qual instituição quer testar.
#
# Exemplos válidos hoje:
# - "cielo"
# - "pagbank"
#
# A Credishop ainda está em fase de debug/padronização,
# então ela NÃO deve ser testada aqui enquanto não tiver motor.
# ============================================================

INSTITUICAO = "cielo"  # <-- Mude aqui para testar outra instituição

PASTA_SAIDA = r"C:\Users\yan.fernandes\Desktop\conciliador\saida_testes"


CONFIG_TESTES = {
    "cielo": {
        "caminho_erp": (
            r"C:\Users\yan.fernandes\Documents\Conciliador PROD\conciliação cielo\Análise de Titulos de Cartão de Terceiros - SFR (3).csv"
            
        ),
        "caminho_instituicao": (
            r"C:\Users\yan.fernandes\Documents\Conciliador PROD\conciliação cielo\Recebiveis_cielo_detalhe-20250501-20250507-1-1-xlsx.xlsx"
            
        ),
    },

    "pagbank": {
        "caminho_erp": (
            r"C:\Users\yan.fernandes\Documents\Conciliador PROD\pagbank\Análise de Titulos de Cartão de Terceiros - SFR (14).csv"
        ),
        "caminho_instituicao": (
            r"C:\Users\yan.fernandes\Documents\Conciliador PROD\pagbank\PagBank_2026-04-17_17-24-39-detalhado.csv"
            
        ),
    },

    "credishop": {
        "caminho_erp": (
            r"C:\Users\yan.fernandes\Desktop\Conciliador PROD\conciliação credshop\Análise de Titulos de Cartão de Terceiros - SFR (3).csv"
            
        ),
        "caminho_instituicao": (
            r"C:\Users\yan.fernandes\Desktop\Conciliador PROD\conciliação credshop\creditos-efetuar-20250501-20250507.csv"
            
        ),
    },

"santander": {
    "caminho_erp": (
        r"C:\Users\yan.fernandes\Documents\Conciliador PROD\conciliação santander\Análise de Titulos de Cartão de Terceiros - SFR.csv"
    ),
    "caminho_instituicao": (
        r"C:\Users\yan.fernandes\Documents\Conciliador PROD\conciliação santander\Recebivel_Completos_9784485_20250101_20250131_17b71b847b834144add843c70f2feea1.xlsx"
    ),
},
}


def obter_configuracao_teste(instituicao):
    instituicao = instituicao.lower().strip()

    if instituicao not in CONFIG_TESTES:
        raise ValueError(f"Configuração de teste não encontrada para: {instituicao}")

    return CONFIG_TESTES[instituicao]


# ============================================================
# EXIBIÇÃO DO RESULTADO DO TESTE
# ============================================================
# Esta função apenas imprime no terminal um resumo do que aconteceu.
# Ela não altera dados, não concilia e não gera arquivos.
# ============================================================

def exibir_resumo_resultado(resultado):
    # DataFrames gerados pelo fluxo
    df_erp = resultado["df_erp_padronizado"]
    df_instituicao = resultado["df_instituicao_padronizado"]
    df_conciliado = resultado["df_conciliado"]

    # Informações dos arquivos finais
    relatorio = resultado["relatorio"]
    download = resultado["download"]

    # Resultado da validação automática do fluxo
    validacao = resultado["validacao"]

    print("\n================ ERP PADRONIZADO ================")
    print(f"Linhas: {df_erp.shape[0]} | Colunas: {df_erp.shape[1]}")

    print("\n================ INSTITUICAO PADRONIZADA ================")
    print(f"Linhas: {df_instituicao.shape[0]} | Colunas: {df_instituicao.shape[1]}")

    print("\n================ RESULTADO DA CONCILIACAO ================")
    print(df_conciliado["status_conciliacao"].value_counts())

    print("\n================ RELATORIO FINAL ================")
    print(f"Arquivo base gerado: {relatorio['caminho_saida']}")
    print(f"Arquivo final download: {download['caminho_arquivo']}")
    print(f"Nome final: {download['nome_arquivo']}")
    print(f"Conciliados: {relatorio['qtd_conciliados']}")
    print(f"Nao conciliados: {relatorio['qtd_nao_conciliados']}")
    print(f"Valor liquido conciliado: {relatorio['valor_liquido_conciliado']}")
    print(f"Valor liquido nao conciliado: {relatorio['valor_liquido_nao_conciliado']}")

    print("\n================ VALIDACAO DO FLUXO ================")

    if validacao["valido"]:
        print("Fluxo valido.")
    else:
        print("Fluxo invalido.")

    if validacao["erros"]:
        print("\nErros:")
        for erro in validacao["erros"]:
            print(f"- {erro}")

    if validacao["avisos"]:
        print("\nAvisos:")
        for aviso in validacao["avisos"]:
            print(f"- {aviso}")

    if not validacao["erros"] and not validacao["avisos"]:
        print("Nenhum erro ou aviso encontrado.")


# ============================================================
# EXECUÇÃO PRINCIPAL DO TESTE
# ============================================================
# Aqui o teste chama o core oficial.
#
# O teste.py não precisa saber:
# - qual padronizador usar
# - qual motor usar
# - como ler CSV ou XLSX
# - como gerar o relatório
# - como preparar o download
#
# Tudo isso é responsabilidade dos módulos.
# ============================================================

def main():
    print("\n====================================================")
    print("INICIANDO TESTE DO FLUXO MODULAR")
    print("====================================================")
    print(f"Instituicao selecionada: {INSTITUICAO}")

    config_teste = obter_configuracao_teste(INSTITUICAO)

    resultado = executar_fluxo_conciliacao(
        instituicao=INSTITUICAO,
        caminho_erp=config_teste["caminho_erp"],
        caminho_instituicao=config_teste["caminho_instituicao"],
        pasta_saida=PASTA_SAIDA,
        salvar_intermediarios=True,
    )

    exibir_resumo_resultado(resultado)

    print("\n====================================================")
    print("TESTE FINALIZADO COM SUCESSO")
    print("====================================================")


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()