"""Tela do caderno e o botão Caderno da cena, com o driver `dummy` do SDL."""

import pygame
import pytest

from politicalizando.conteudo import carregar_textos
from politicalizando.dominio.caderno import Caderno
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.fichas import Fichas
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.partida import Partida
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.dominio.textos import Textos
from politicalizando.estados.caderno import CONVERSAS, FICHAS, FONTES, ITENS, EstadoCaderno
from politicalizando.estados.cena import EstadoCena

# Cena, caderno e fichas de exemplo, neutros e provisórios: só existem nos testes.
CENAS = Cenas.de_toml(
    """
inicio = "exemplo.sala"

[recusas]
olhar = ["exemplo.recusa"]
usar = ["exemplo.recusa"]
falar = ["exemplo.recusa"]

[[cenas.exemplo.sala.objetos]]
id = "guia"
nome = "exemplo.guia.nome"
area = [20, 40, 40, 40]
falar = [{ marcar_flag = "exemplo.guia.posicao" }, { fala = "exemplo.recusa" }]
usar = [{ dar_item = "folheto" }]
"""
)
CADERNO = Caderno.de_toml(
    """
[itens]
folheto = "exemplo.item.folheto"

[[entradas]]
id = "guia"
texto = "exemplo.guia.disse"
origem = "opiniao"
de = "exemplo.guia.nome"
se = ["exemplo.guia.posicao"]

[[entradas]]
id = "horario"
texto = "exemplo.horario"
origem = "fato"
fontes = [{ autor = "Prefeitura", titulo = "Horários", ano = 2026, do_jogo = true }]
se = ["exemplo.guia.posicao"]
"""
)


def _ficha(corrente: str) -> str:
    outra = next(c for c in CORRENTES if c != corrente)
    return f"""
[fichas.{corrente}]
se = ["exemplo.guia.posicao"]
ideia_central = "exemplo.ficha.corpo"
valores = ["exemplo.ficha.corpo"]
estado = "exemplo.ficha.corpo"
mercado = "exemplo.ficha.corpo"
sociedade = "exemplo.ficha.corpo"
origem = "exemplo.ficha.corpo"
pensadores = ["exemplo.ficha.corpo"]
proposta = "exemplo.ficha.corpo"
confusoes = ["exemplo.ficha.corpo"]
diferencas_internas = ["exemplo.ficha.vertente_1", "exemplo.ficha.vertente_2"]
criticas = [
  {{ texto = "exemplo.ficha.corpo", de = "{outra}" }},
  {{ texto = "exemplo.ficha.corpo", de = "outras" }},
]
fontes = [{{ autor = "Exemplo, Autor", titulo = "Obra", ano = 2000, editora = "Ed." }}]
"""


FICHAS_EXEMPLO = Fichas.de_toml(_ficha("socialismo") + _ficha("liberalismo"))
TEXTOS = Textos.de_toml(
    "\n".join(
        f'[exemplo.{nome}]\ntexto = "Exemplo {nome}"'
        for nome in ("recusa", "guia.nome", "guia.disse", "horario", "item.folheto")
    )
    + '\n[exemplo.ficha.corpo]\ntexto = "Um texto de ficha de exemplo, comprido o bastante para '
    'ocupar mais de uma linha na área do caderno."\n'
    + '[exemplo.ficha.vertente_1]\ntexto = "Vertente 1"\n'
    + '[exemplo.ficha.vertente_2]\ntexto = "Vertente 2"\n'
)


@pytest.fixture
def jogo_exemplo(jogo):
    jogo.textos = Textos({**carregar_textos(), **TEXTOS})
    jogo.interacao = Interacao(CENAS, Roteiros(), Dialogos())
    jogo.caderno = CADERNO
    jogo.fichas = FICHAS_EXEMPLO
    return jogo


def tecla(tela, key, mod=0):
    tela.tratar_evento(pygame.Event(pygame.KEYDOWN, key=key, mod=mod))
    tela.atualizar(0)


def clicar(tela, x, y):
    tela.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=(x, y)))
    tela.tratar_evento(pygame.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1))
    tela.atualizar(0)


@pytest.fixture
def cena(jogo_exemplo):
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    jogo_exemplo.trocar_estado(tela)
    tela.atualizar(0)
    return tela


def abrir(cena) -> EstadoCaderno:
    tecla(cena, pygame.K_c)
    caderno = cena.jogo.estado
    assert isinstance(caderno, EstadoCaderno)
    return caderno


def textos_da_tela(caderno) -> list[str]:
    return [texto for texto, _ in caderno.linhas()]


def conversar(cena):
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_3)
    tecla(cena, pygame.K_RETURN)
    assert not cena.partida.ocupada


def test_caderno_abre_desde_o_inicio_com_as_abas_vazias(cena, jogo_exemplo):
    cena.desenhar(jogo_exemplo.tela)
    caderno = abrir(cena)
    vazio = jogo_exemplo.textos["caderno.vazio"].texto
    for aba in (FICHAS, CONVERSAS, FONTES, ITENS):
        tecla(caderno, pygame.K_1 + aba)
        assert caderno.aba == aba
        assert textos_da_tela(caderno) == [vazio]
        caderno.desenhar(jogo_exemplo.tela)


def test_botao_caderno_abre_pelo_mouse(cena, jogo_exemplo):
    clicar(cena, *cena.botao_caderno.center)
    assert isinstance(jogo_exemplo.estado, EstadoCaderno)


def test_caderno_nao_abre_durante_uma_fala(cena, jogo_exemplo):
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_3)
    assert cena.partida.ocupada
    tecla(cena, pygame.K_c)
    assert jogo_exemplo.estado is cena


def test_conversas_e_fontes_mostram_a_origem(cena, jogo_exemplo):
    conversar(cena)
    caderno = abrir(cena)
    tecla(caderno, pygame.K_RIGHT)
    assert caderno.aba == CONVERSAS
    assert textos_da_tela(caderno) == ["Exemplo guia.nome", "Exemplo guia.disse"]
    tecla(caderno, pygame.K_RIGHT)
    fato = jogo_exemplo.textos["caderno.origem.fato"].texto
    do_jogo = jogo_exemplo.textos["caderno.fonte.do_jogo"].texto
    linhas = textos_da_tela(caderno)
    assert linhas[:2] == [fato, "Exemplo horario"]
    assert linhas[2] == f"Prefeitura. Horários, 2026. ({do_jogo})"
    caderno.desenhar(jogo_exemplo.tela)


def test_itens_mostram_o_nome(cena):
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_2)
    caderno = abrir(cena)
    tecla(caderno, pygame.K_4)
    assert textos_da_tela(caderno) == ["Exemplo item.folheto"]


def test_fichas_saem_na_ordem_fixa_e_abrem_com_os_itens(cena, jogo_exemplo):
    conversar(cena)
    caderno = abrir(cena)
    nomes = [jogo_exemplo.textos[f"corrente.{c}"].texto for c in ("liberalismo", "socialismo")]
    assert textos_da_tela(caderno) == nomes, "a ordem das correntes, não a do arquivo"
    tecla(caderno, pygame.K_DOWN)
    tecla(caderno, pygame.K_RETURN)
    assert caderno.ficha_aberta.corrente == "socialismo"
    linhas = textos_da_tela(caderno)
    assert linhas[0] == nomes[1]
    for titulo in (
        "ficha.item.ideia_central",
        "ficha.item.diferencas_internas",
        "ficha.item.fontes",
    ):
        assert jogo_exemplo.textos[titulo].texto in linhas
    assert "Vertente 2" in linhas
    caderno.desenhar(jogo_exemplo.tela)

    tecla(caderno, pygame.K_ESCAPE)
    assert caderno.ficha_aberta is None
    assert jogo_exemplo.estado is caderno, "o primeiro Esc só fecha a ficha"


def test_rolagem_da_ficha(cena, jogo_exemplo):
    conversar(cena)
    caderno = abrir(cena)
    tecla(caderno, pygame.K_RETURN)
    total = len(caderno.linhas())
    assert total > caderno.linhas_visiveis
    tecla(caderno, pygame.K_DOWN)
    assert caderno.rolagem == 1
    tecla(caderno, pygame.K_PAGEDOWN)
    caderno.tratar_evento(pygame.Event(pygame.MOUSEWHEEL, x=0, y=-100))
    assert caderno.rolagem == total - caderno.linhas_visiveis, "para no fim"
    caderno.desenhar(jogo_exemplo.tela)
    tecla(caderno, pygame.K_PAGEUP)
    caderno.tratar_evento(pygame.Event(pygame.MOUSEWHEEL, x=0, y=100))
    assert caderno.rolagem == 0, "para no começo"


def test_ficha_abre_pelo_mouse_e_aba_troca_pelo_clique(cena):
    conversar(cena)
    caderno = abrir(cena)
    clicar(caderno, caderno.area.x + 5, caderno.area.y + caderno.altura_linha + 2)
    assert caderno.ficha_aberta.corrente == "socialismo"
    clicar(caderno, *caderno.botoes_abas[FONTES].center)
    assert caderno.aba == FONTES
    assert caderno.ficha_aberta is None


def test_esc_e_c_voltam_para_a_cena(cena, jogo_exemplo):
    for fechar in (pygame.K_ESCAPE, pygame.K_c):
        caderno = abrir(cena)
        tecla(caderno, fechar)
        assert jogo_exemplo.estado is cena


def test_caderno_do_jogo_real_abre(jogo):
    tela = EstadoCena(jogo, Partida.nova(jogo.interacao))
    jogo.trocar_estado(tela)
    tela.atualizar(0)
    tela.partida.confirmar()
    tela.atualizar(0)
    tela.partida.confirmar()
    tela.atualizar(0)
    caderno = abrir(tela)
    for aba in range(4):
        tecla(caderno, pygame.K_1 + aba)
        caderno.desenhar(jogo.tela)
