from modulo_3_padronizacao.cielo_padronizador import padronizar_cielo
from modulo_3_padronizacao.pagbank_padronizador import padronizar_pagbank
from modulo_3_padronizacao.santander_padronizador import padronizar_santander
from modulo_4_conciliacao.motor_santander import conciliar_santander
from modulo_4_conciliacao.motor_cielo import conciliar_padronizado
from modulo_4_conciliacao.motor_pagbank import conciliar_pagbank
from modulo_3_padronizacao.credishop_padronizador import padronizar_credishop
from modulo_4_conciliacao.motor_credishop import conciliar_credishop

INSTITUICOES = {
    "cielo": {
        "nome": "Cielo",
        "padronizador": padronizar_cielo,
        "conciliador": conciliar_padronizado,
        "formatos_aceitos": ["xlsx", "xls"],
    },

    "pagbank": {
        "nome": "PagBank",
        "padronizador": padronizar_pagbank,
        "conciliador": conciliar_pagbank,
        "formatos_aceitos": ["csv"],
    },

    "credishop": {
        "nome": "Credishop",
        "padronizador": padronizar_credishop,
        "conciliador": conciliar_credishop,
        "formatos_aceitos": ["csv"],
    },

    "santander": {
    "nome": "Santander",
    "padronizador": padronizar_santander,
    "conciliador": conciliar_santander,
    "formatos_aceitos": ["xlsx", "xls"],
},
}


def obter_configuracao_instituicao(nome_instituicao):
    nome_instituicao = nome_instituicao.lower().strip()

    if nome_instituicao not in INSTITUICOES:
        raise ValueError(f"Instituição não cadastrada: {nome_instituicao}")

    return INSTITUICOES[nome_instituicao]


def obter_padronizador_instituicao(nome_instituicao):
    configuracao = obter_configuracao_instituicao(nome_instituicao)

    return configuracao["padronizador"]


def obter_conciliador_instituicao(nome_instituicao):
    configuracao = obter_configuracao_instituicao(nome_instituicao)

    return configuracao["conciliador"]


def obter_formatos_aceitos(nome_instituicao):
    configuracao = obter_configuracao_instituicao(nome_instituicao)

    return configuracao["formatos_aceitos"]