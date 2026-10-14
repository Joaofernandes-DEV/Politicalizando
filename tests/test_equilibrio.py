"""Salvaguardas de equilíbrio nas mecânicas (briefing, seção 6.1).

E4 entra aqui; E2, E3 e E5 chegam no PR `feat/checagem-de-fontes`.
"""

import pytest

from politicalizando.conteudo import carregar_cenas, carregar_textos
from politicalizando.dominio.textos import Textos

# Trechos que indicam uma corrente no texto (sem acento e em minúsculas, para comparar).
TERMOS_DE_CORRENTE = ("liberal", "conservador", "socialis", "social-democra", "socialdemocra")


def _normalizar(texto: str) -> str:
    return texto.lower().translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))


def recusas_que_citam_correntes(recusas: set[str], textos: Textos) -> list[str]:
    return sorted(
        id_texto
        for id_texto in recusas
        if any(termo in _normalizar(textos[id_texto].texto) for termo in TERMOS_DE_CORRENTE)
    )


@pytest.mark.parametrize(
    "frase",
    [
        "Uma ideia bem liberal.",
        "Isso é coisa de Conservador.",
        "Parece socialismo.",
        "Bem social-democrata.",
        "Socialdemocracia pura.",
    ],
)
def test_e4_recusa_que_cita_uma_corrente_e_acusada(frase):
    textos = Textos.de_toml(f'[exemplo.recusa]\ntexto = "{frase}"')
    assert recusas_que_citam_correntes({"exemplo.recusa"}, textos) == ["exemplo.recusa"]


def test_e4_recusa_neutra_passa():
    textos = Textos.de_toml('[exemplo.recusa]\ntexto = "Não há nada de especial aqui."')
    assert recusas_que_citam_correntes({"exemplo.recusa"}, textos) == []


def test_e4_recusas_do_jogo_nunca_falam_de_correntes():
    recusas = set().union(*carregar_cenas().recusas.values())
    assert recusas_que_citam_correntes(recusas, carregar_textos()) == []
