# Checkpoint - Instituições Validadas

## Status

Fluxo modular validado com sucesso para:

- Cielo
- PagBank
- Credishop

## Arquitetura atual

### Módulo 1 - Seleção
Responsável pelo cadastro das instituições, padronizadores, conciliadores e formatos aceitos.

### Módulo 2 - Leitura
Responsável por ler arquivos ERP e arquivos das instituições.

### Módulo 3 - Padronização
Responsável por transformar arquivos brutos em colunas internas padronizadas.

### Módulo 4 - Conciliação
Responsável por aplicar o motor específico de cada instituição.

### Módulo 5 - Relatório
Responsável por gerar relatório final genérico.

### Módulo 6 - Download
Responsável por preparar o arquivo final com nome padronizado.

### Core
Responsável por orquestrar o fluxo completo e validar o resultado.

## Instituições

### Cielo
- Entrada: XLSX
- Padronizador: `cielo_padronizador.py`
- Motor: `motor_cielo.py`
- Status: validada

### PagBank
- Entrada: CSV
- Padronizador: `pagbank_padronizador.py`
- Motor: `motor_pagbank.py`
- Status: validada

### Credishop
- Entrada: CSV
- Padronizador: `credishop_padronizador.py`
- Motor: `motor_credishop.py`
- Status: validada

## Regras importantes

- O ERP é sempre CSV.
- O relatório é genérico.
- O download é genérico.
- Cada instituição pode ter padronizador próprio.
- Cada instituição pode ter motor próprio.
- Aluguel e estorno não devem ficar na aba "Não conciliados"; devem ir para abas especiais.
- O nome do arquivo final usa instituição + data/hora de geração.

## Próximo passo

Adicionar nova instituição ou iniciar a interface web usando `executar_fluxo_conciliacao`.