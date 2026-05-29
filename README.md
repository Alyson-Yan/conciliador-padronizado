# Conciliador Modular

Sistema web modular para conciliação entre arquivos do ERP e arquivos de instituições financeiras/adquirentes.

O projeto recebe dois arquivos, padroniza os dados, executa a conciliação e gera um relatório final em Excel com abas de conciliados, não conciliados, eventos especiais e resumo financeiro.

## Instituições validadas

* Cielo
* GetNet
* PagBank
* CredShop

## Formatos aceitos

| Origem   | Formato |
| -------- | ------- |
| ERP      | `.csv`  |
| Cielo    | `.xlsx` |
| GetNet   | `.xlsx` |
| PagBank  | `.csv`  |
| CredShop | `.csv`  |

## Fluxo principal

1. Seleção da instituição financeira/adquirente
2. Upload do arquivo ERP e do arquivo da instituição
3. Leitura dos arquivos
4. Padronização dos dados do ERP
5. Padronização dos dados da instituição
6. Execução da conciliação
7. Separação entre conciliados, não conciliados e eventos especiais
8. Geração do relatório final em Excel
9. Preparação do arquivo para download

## Estrutura do projeto

```text
conciliador/
│
├── app/
│   ├── main.py
│   ├── routes/
│   │   └── conciliacao_routes.py
│   └── services/
│       └── conciliacao_service.py
│
├── core/
│   └── fluxo_conciliacao.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── modulo_1_selecao/
│   └── instituicoes.py
│
├── modulo_2_upload/
│   └── leitor_arquivos.py
│
├── modulo_3_padronizacao/
│   ├── erp_padronizador.py
│   ├── cielo_padronizador.py
│   ├── getnet_padronizador.py
│   ├── pagbank_padronizador.py
│   └── credishop_padronizador.py
│
├── modulo_4_conciliacao/
│   ├── motor_cielo.py
│   ├── motor_getnet.py
│   ├── motor_pagbank.py
│   └── motor_credishop.py
│
├── modulo_5_relatorio/
│   └── gerar_relatorio.py
│
├── modulo_6_download/
│   └── preparar_download.py
│
├── tests_manuais/
│   └── teste_fluxo.py
│
├── requirements.txt
├── iniciar_servidor.bat
└── README.md
```

## Responsabilidade de cada módulo

### `app/`

Contém a aplicação FastAPI.

* `main.py`: ponto de entrada da API e da interface web.
* `routes/`: rotas HTTP da aplicação.
* `services/`: camada que recebe os arquivos da web, salva temporariamente e chama o fluxo principal.

### `frontend/`

Contém a interface visual do sistema.

* `index.html`: estrutura da tela.
* `style.css`: aparência da aplicação.
* `script.js`: lógica da tela, seleção de instituição, validação de arquivos, envio para a API e download do relatório.

### `core/`

Contém a orquestração principal do fluxo de conciliação.

O arquivo `fluxo_conciliacao.py` coordena:

* leitura dos arquivos;
* escolha da instituição;
* padronização;
* conciliação;
* geração do relatório;
* preparação do download.

### `modulo_1_selecao/`

Cadastro das instituições disponíveis.

Define:

* nome da instituição;
* função de padronização;
* função de conciliação;
* formatos aceitos.

### `modulo_2_upload/`

Responsável pela leitura dos arquivos enviados.

Também valida os formatos permitidos:

* ERP sempre `.csv`;
* Cielo e GetNet em `.xlsx`;
* PagBank e CredShop em `.csv`.

### `modulo_3_padronizacao/`

Transforma os arquivos originais em um formato padrão interno.

Cada instituição tem um padronizador próprio, pois cada arquivo possui layout e nomes de colunas diferentes.

### `modulo_4_conciliacao/`

Contém os motores de conciliação.

Cada motor compara os dados padronizados da instituição com os dados padronizados do ERP, usando critérios como:

* valor;
* data;
* autorização;
* NSU;
* parcela;
* total de parcelas.

### `modulo_5_relatorio/`

Gera o relatório final em Excel.

O relatório pode conter:

* aba `Conciliados`;
* aba `Não conciliados`;
* aba `Cancelamentos`;
* aba `Aluguel e Tarifas`;
* aba `Estornos`;
* aba `Resumo`.

O resumo também pode incluir grupos de chaves ERP conciliadas, separadas em blocos de 2000 títulos, com quantidade, valor bruto e valor líquido por grupo.

### `modulo_6_download/`

Prepara o arquivo final para download pela interface web.

### `tests_manuais/`

Contém scripts auxiliares para testes manuais do fluxo e depuração de arquivos.

## Como instalar

Crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\activate
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

## Como executar

Pelo terminal:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ou pelo arquivo:

```text
iniciar_servidor.bat
```

## Como acessar

No próprio computador:

```text
http://127.0.0.1:8000
```

Na rede local:

```text
http://IP-DA-MAQUINA:8000
```

Exemplo:

```text
http://192.168.1.214:8000
```

## Dependências principais

* FastAPI
* Uvicorn
* pandas
* openpyxl
* rapidfuzz
* python-multipart
* numpy

## Observações

O sistema foi desenvolvido para uso local ou em rede interna.

Caso seja necessário expor o sistema fora da rede da empresa, é recomendado adicionar autenticação, controle de acesso e configuração segura de publicação.
