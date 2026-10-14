"""Salvaguardas de equilíbrio nas mecânicas e no conteúdo (briefing, seções 5 e 6.1).

Aqui ficam o E4 e o equilíbrio das fichas (mesmo modelo, tamanho parecido, as 4 correntes);
E2, E3 e E5 chegam no PR `feat/checagem-de-fontes`.
"""

import pytest

from politicalizando.conteudo import carregar_cenas, carregar_fichas, carregar_textos
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.fichas import Fichas
from politicalizando.dominio.textos import Textos

# A ficha mais longa pode ter no máximo 1,3× os caracteres da mais curta.
LIMITE_DE_TAMANHO_DAS_FICHAS = 1.3

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


# --- Fichas: tamanho parecido e as 4 correntes ----------------------------------------------


def tamanhos_das_fichas(fichas: Fichas, textos: Textos) -> dict[str, int]:
    """Caracteres de todos os textos de cada ficha."""
    return {
        corrente: sum(len(textos[id_texto].texto) for id_texto in ficha.ids_de_texto())
        for corrente, ficha in fichas.items()
    }


def desequilibrio_das_fichas(fichas: Fichas, textos: Textos) -> str | None:
    """Uma mensagem se a ficha mais longa passa do limite em relação à mais curta."""
    tamanhos = tamanhos_das_fichas(fichas, textos)
    if len(tamanhos) < 2:
        return None
    maior = max(tamanhos, key=tamanhos.get)
    menor = min(tamanhos, key=tamanhos.get)
    if tamanhos[maior] > LIMITE_DE_TAMANHO_DAS_FICHAS * tamanhos[menor]:
        limite = f"{LIMITE_DE_TAMANHO_DAS_FICHAS:g}×".replace(".", ",")
        return (
            f"{maior} ({tamanhos[maior]}) passa de {limite} {menor} ({tamanhos[menor]}): {tamanhos}"
        )
    return None


# Ficha fictícia: a ideia central varia de tamanho; todos os outros itens usam o mesmo texto
# curto "exemplo.{c}.x".
_FICHA = """
[fichas.{c}]
ideia_central = "exemplo.{c}.ideia"
valores = ["exemplo.{c}.x"]
estado = "exemplo.{c}.x"
mercado = "exemplo.{c}.x"
sociedade = "exemplo.{c}.x"
origem = "exemplo.{c}.x"
pensadores = ["exemplo.{c}.x"]
proposta = "exemplo.{c}.x"
confusoes = ["exemplo.{c}.x"]
criticas = [{{ texto = "exemplo.{c}.x", de = "outras" }}, {{ texto = "exemplo.{c}.y", de = "{o}" }}]
fontes = [{{ autor = "Exemplo, Autor", titulo = "Obra", ano = 2000, editora = "Ed." }}]
"""


def _fichas_e_textos(tamanhos: dict[str, int]) -> tuple[Fichas, Textos]:
    fichas, textos = [], []
    for corrente, tamanho in tamanhos.items():
        outra = next(c for c in CORRENTES if c != corrente)
        fichas.append(_FICHA.format(c=corrente, o=outra))
        textos.append(
            f'[exemplo.{corrente}.ideia]\ntexto = "{"a" * tamanho}"\n'
            f'[exemplo.{corrente}.x]\ntexto = "b"\n'
            f'[exemplo.{corrente}.y]\ntexto = "c"\n'
        )
    return Fichas.de_toml("".join(fichas)), Textos.de_toml("".join(textos))


def test_fichas_de_tamanho_parecido_passam():
    fichas, textos = _fichas_e_textos({"liberalismo": 100, "socialismo": 120})
    assert desequilibrio_das_fichas(fichas, textos) is None


def test_ficha_muito_mais_longa_e_acusada():
    fichas, textos = _fichas_e_textos({"liberalismo": 100, "socialismo": 200})
    mensagem = desequilibrio_das_fichas(fichas, textos)
    assert mensagem is not None
    assert mensagem.startswith("socialismo")


def test_fichas_do_jogo_tem_tamanho_parecido():
    assert desequilibrio_das_fichas(carregar_fichas(), carregar_textos()) is None


@pytest.mark.xfail(
    strict=True,
    reason="As fichas reais entram na Fase 4. Quando as 4 chegarem, este teste passa e o "
    "xfail estrito acusa: remova a marcação para o teste virar obrigatório.",
)
def test_ha_uma_ficha_para_cada_uma_das_4_correntes():
    assert list(carregar_fichas()) == list(CORRENTES)
