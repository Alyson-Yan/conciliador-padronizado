import pandas as pd
from rapidfuzz import process, fuzz

def encontrar_melhor_correspondencia_com_pontuacao(
    row,
    df_origem,
    coluna_erp
):

    correspondencias = process.extract(
        str(row["AUTORIZAÇÃO"]),
        df_origem[coluna_erp].astype(str),
        scorer=fuzz.ratio,
        limit=10
    )

    correspondencias_validas = [
        (texto, score, idx)
        for texto, score, idx in correspondencias
        if score >= 80
    ]

    if not correspondencias_validas:
        return pd.Series(
            [None, None, None, "Não Conciliado", 99]
        )

    melhor_resultado = None
    menor_pontuacao = float("inf")

    for melhor_correspondencia, _, _ in correspondencias_validas:

        filtro = df_origem[
            df_origem[coluna_erp] == melhor_correspondencia
        ]

        if filtro.empty:
            continue

        for _, linha_correspondente in filtro.iterrows():

            valor_erp = linha_correspondente["Valor"]
            data_erp = linha_correspondente["Emissão"]
            parcela_erp = linha_correspondente["Parcela"]
            total_parcelas_erp = linha_correspondente["Total_Parcelas"]

            status = ["Conciliado"]
            pontuacao = 0

            if abs(
                row["VALOR DA PARCELA"] - valor_erp
            ) > 0.10:

                status.append(
                    "Divergência de Valor"
                )
                pontuacao += 15

            if abs(
                (
                    row["DATA DA VENDA"] -
                    data_erp
                ).days
            ) > 1:

                status.append(
                    "Divergência de Data"
                )
                pontuacao += 5

            if row["PARCELA"] != parcela_erp:
                status.append(
                    "Divergência de Parcela"
                )
                pontuacao += 10

            if (
                row["TOTAL_PARCELAS"]
                !=
                total_parcelas_erp
            ):
                status.append(
                    "Divergência de Total de Parcelas"
                )
                pontuacao += 15

            if pontuacao < menor_pontuacao:

                menor_pontuacao = pontuacao

                melhor_resultado = (
                    linha_correspondente[coluna_erp],
                    linha_correspondente["Chave"],
                    valor_erp,
                    " com ".join(status)
                    if len(status) > 1
                    else status[0],
                    pontuacao
                )

    if melhor_resultado:
        return pd.Series(melhor_resultado)

    return pd.Series(
        [None, None, None, "Não Conciliado", 99]
    )


def encontrar_melhor_correspondencia_com_pontuacao_nsu(row, df_origem):
            correspondencias = process.extract(
                str(row["NÚMERO COMPROVANTE DE VENDA (NSU)"]),
                df_origem["NSU"].astype(str),
                scorer=fuzz.ratio,
                limit=10
            )

            correspondencias_validas = [(texto, score, idx) for texto, score, idx in correspondencias if score >= 80]

            print(f"\n Buscando correspondência para: {row['NÚMERO COMPROVANTE DE VENDA (NSU)']}")
            print("Correspondências válidas (score >= 80):", correspondencias_validas)

            if not correspondencias_validas:
                return pd.Series([None, None, None, "Não Conciliado", 99])

            melhor_resultado = None
            menor_pontuacao = float("inf")

            for melhor_correspondencia, melhor_pontuacao, _ in correspondencias_validas:
                filtro = df_origem[df_origem["NSU"] == melhor_correspondencia]

                if filtro.empty:
                    print(f"⚠ Correspondência '{melhor_correspondencia}' não encontrada no DataFrame.")
                    continue

                #  Itera sobre todas as linhas com o mesmo valor
                for _, linha_correspondente in filtro.iterrows():
                    valor_erp = linha_correspondente["Valor"]
                    data_erp = linha_correspondente["Emissão"]
                    parcela_erp = linha_correspondente["Parcela"]
                    total_parcelas_erp = linha_correspondente["Total_Parcelas"]

                    status = ["Conciliado"]
                    pontuacao = 0

                    if abs(row["VALOR DA PARCELA"] - valor_erp) > 0.10:
                        status.append("Divergência de Valor")
                        pontuacao += 15

                    if abs((row["DATA DA VENDA"] - data_erp).days) > 1:
                        status.append("Divergência de Data")
                        pontuacao += 5

                    if row["PARCELA"] != parcela_erp:
                        status.append("Divergência de Parcela")
                        pontuacao += 10

                    if row["TOTAL_PARCELAS"] != total_parcelas_erp:
                        status.append("Divergência de Total de Parcelas")
                        pontuacao += 15

                    if pontuacao < menor_pontuacao:
                        menor_pontuacao = pontuacao
                        melhor_resultado = (
                            linha_correspondente["NSU"],
                            linha_correspondente["Chave"],
                            valor_erp,
                            " e ".join(status) if len(status) > 1 else status[0],
                            pontuacao
                        )

            if melhor_resultado:
                print(" Melhor resultado escolhido:", melhor_resultado)
                return pd.Series(melhor_resultado)
            else:
                print(" Nenhuma correspondência com pontuação aceitável.")
                return pd.Series([None, None, None, "Não Conciliado", 99])

def selecionar_melhor_por_pontuacao_com_autorizacao_e_nsu(row, df_erp_base, tolerancia_dias=5, tolerancia_valor=0.20, incluir_detalhes=False):
            candidatos = df_erp_base[
                (df_erp_base["Emissão"] - row["DATA DA VENDA"]).abs().dt.days <= tolerancia_dias
            ]

            candidatos = candidatos[
                (candidatos["Valor"] - row["VALOR DA PARCELA"]).abs() <= tolerancia_valor
            ]

            candidatos = candidatos[
                (candidatos["Parcela"] == row["PARCELA"]) &
                (candidatos["Total_Parcelas"] == row["TOTAL_PARCELAS"])
            ]

            if candidatos.empty:
                if incluir_detalhes:
                    return pd.Series([None, None, None, None, None, None, "Não Conciliado", 999])
                else:
                    return pd.Series([None, None, None, None, "Não Conciliado", 999])

            melhor_resultado = None
            menor_pontuacao = float("inf")

            for _, linha in candidatos.iterrows():
                if pd.isna(linha["Emissão"]) or pd.isna(row["DATA DA VENDA"]):
                    dias_dif = 999
                else:
                    dias_dif = abs((linha["Emissão"] - row["DATA DA VENDA"]).days)
                    
                valor_dif = abs(linha["Valor"] - row["VALOR DA PARCELA"])

                aut_sant = str(row["AUTORIZAÇÃO"]).strip()
                aut_erp = str(linha["Autorização"]).strip()
                nsu_sant = str(row["NÚMERO COMPROVANTE DE VENDA (NSU)"]).strip()
                nsu_erp = str(linha["NSU"]).strip()

                if aut_sant == aut_erp or nsu_sant == nsu_erp:
                    sim_autorizacao = 100
                    sim_nsu = 100
                else:
                    sim_autorizacao = fuzz.ratio(aut_sant, aut_erp)
                    sim_nsu = fuzz.ratio(nsu_sant, nsu_erp)

                pontuacao = dias_dif * 100 + valor_dif * 100 + (200 - (sim_autorizacao + sim_nsu))
                if "Pessoa do Título" in linha and linha["Pessoa do Título"] != "Getnet Adquirencia E Servicos Para Meios de Pagamento S.a.":
                    pontuacao += 101

                if pontuacao < menor_pontuacao:
                    menor_pontuacao = pontuacao
                    
                    # --- LÓGICA DO STATUS DINÂMICO CORRIGIDA ---
                    status_lista = ["Conciliado"]
                    
                    if valor_dif > 0.10:
                        status_lista.append("Divergência de Valor")
                    
                    if dias_dif > 1 and dias_dif != 999:
                        status_lista.append("Divergência de Data")
                    elif dias_dif == 999:
                        status_lista.append("Data Ausente")

                    # NOVA VERIFICAÇÃO: Compara se os campos são diferentes de fato
                    if (aut_sant != aut_erp) and (nsu_sant != nsu_erp):
                        status_lista.append("Divergência de NSU/Autorização")
                    elif aut_sant != aut_erp:
                        status_lista.append("Divergência de Autorização")
                    elif nsu_sant != nsu_erp:
                        status_lista.append("Divergência de NSU")
                        
                    status_final = " e ".join(status_lista) if len(status_lista) > 1 else status_lista[0]

                    melhor_resultado = (
                        linha["Autorização"],
                        linha["NSU"],
                        linha["Chave"],
                        linha["Valor"],
                        dias_dif,
                        valor_dif,
                        status_final, 
                        round(pontuacao, 2)
                    )

            if melhor_resultado:
                if incluir_detalhes:
                    return pd.Series(melhor_resultado)
                else:
                    return pd.Series(melhor_resultado[:4] + melhor_resultado[-2:])
            else:
                if incluir_detalhes:
                    return pd.Series([None, None, None, None, None, None, "Não Conciliado", 999])
                else:
                    return pd.Series([None, None, None, None, "Não Conciliado", 999])