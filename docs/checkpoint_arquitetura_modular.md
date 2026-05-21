# Checkpoint - Arquitetura Modular do Conciliador

## Status atual

A arquitetura modular foi validada com sucesso para:

- Cielo
- PagBank

## Fluxo validado

1. Seleção da instituição
2. Leitura dos arquivos
3. Padronização do ERP e da instituição
4. Conciliação por motor específico
5. Geração de relatório genérico
6. Preparação de arquivo final para download
7. Validação automática do fluxo

## Instituições funcionando

### Cielo

- Padronizador: `modulo_3_padronizacao/cielo_padronizador.py`
- Motor: `modulo_4_conciliacao/motor_cielo.py`
- Entrada: XLSX

### PagBank

- Padronizador: `modulo_3_padronizacao/pagbank_padronizador.py`
- Motor: `modulo_4_conciliacao/motor_pagbank.py`
- Entrada: CSV

## Regras importantes

- O ERP é sempre CSV.
- O ERP usa padronizador genérico.
- Cada instituição pode ter padronizador próprio.
- Cada instituição pode ter motor próprio.
- O relatório é genérico.
- O download é genérico.
- O `core/fluxo_conciliacao.py` é o orquestrador oficial.
- O `teste.py` deve apenas chamar o fluxo e exibir resumo.

## Próximo passo

Adicionar próxima instituição seguindo o mesmo padrão.