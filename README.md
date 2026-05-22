\# Conciliador Modular



Sistema modular de conciliação entre ERP e instituições financeiras/adquirentes.



\## Instituições validadas



\- Cielo

\- PagBank

\- Credishop

\- Santander



\## Fluxo principal



1\. Seleção da instituição

2\. Leitura dos arquivos

3\. Padronização do ERP e da instituição

4\. Conciliação

5\. Geração do relatório

6\. Preparação do download

7\. Validação do fluxo



\## Estrutura



\- `core/`: orquestração e validação do fluxo

\- `modulo\_1\_selecao/`: cadastro das instituições

\- `modulo\_2\_upload/`: leitura dos arquivos

\- `modulo\_3\_padronizacao/`: padronização dos dados

\- `modulo\_4\_conciliacao/`: motores de conciliação

\- `modulo\_5\_relatorio/`: geração do relatório final

\- `modulo\_6\_download/`: preparação do arquivo final

\- `utils/`: funções auxiliares



\## Arquivo principal de teste



Atualmente o fluxo é testado por `teste.py`.



Futuramente, a interface web deverá chamar:



```python

executar\_fluxo\_conciliacao(...)

