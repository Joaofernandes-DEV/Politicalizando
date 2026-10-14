"""Todo roteiro, diálogo e caso de checagem dos dados é usado por alguma cena.

O inverso (toda referência existe) é conferido ao carregar as cenas, por `conferir_referencias`.
Quando o mapa e os roteiros especiais em Python chegarem, eles também passam a contar como uso.
"""

from politicalizando.conteudo import (
    carregar_cenas,
    carregar_checagem,
    carregar_dialogos,
    carregar_roteiros,
)
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.checagem import Casos
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.roteiro import Roteiros


def sem_uso(
    roteiros: Roteiros, dialogos: Dialogos, cenas: Cenas, casos: Casos | None = None
) -> list[str]:
    nao_usados = [f"roteiro {nome}" for nome in sorted(set(roteiros) - cenas.roteiros_usados())]
    nao_usados += [f"diálogo {nome}" for nome in sorted(set(dialogos) - cenas.dialogos_usados())]
    if casos is not None:
        nao_usados += [f"caso {nome}" for nome in sorted(set(casos) - cenas.checagens_usadas())]
    return nao_usados


def test_roteiro_e_dialogo_sem_cena_sao_acusados():
    roteiros = Roteiros.de_toml(
        "exemplo.usado = [{ esperar = 1 }]\nexemplo.esquecido = [{ esperar = 1 }]"
    )
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\npassos = [{ esperar = 1 }]'
    )
    cenas = Cenas.de_toml(
        '[recusas]\nolhar = ["exemplo.r"]\nusar = ["exemplo.r"]\nfalar = ["exemplo.r"]\n'
        '[cenas.sala]\nentrada = { roteiro = "exemplo.usado" }\n'
        'objetos = [{ id = "a", nome = "exemplo.a", area = [0, 0, 1, 1] }]'
    )
    assert sem_uso(roteiros, dialogos, cenas) == [
        "roteiro exemplo.esquecido",
        "diálogo exemplo.guia",
    ]


CASO_DE_EXEMPLO = """
[casos.exemplo.comentario]
tipo = "fala"
conteudo = "exemplo.t"
classe = "opiniao"
explicacao = "exemplo.e"
"""


def test_caso_de_checagem_sem_cena_e_acusado():
    casos = Casos.de_toml(CASO_DE_EXEMPLO)
    assert sem_uso(Roteiros(), Dialogos(), Cenas(), casos) == ["caso exemplo.comentario"]


def test_nada_do_jogo_fica_sem_uso():
    dados = (carregar_roteiros(), carregar_dialogos(), carregar_cenas(), carregar_checagem())
    assert sem_uso(*dados) == []
