"""Tela do mapa e o botão Mapa da cena, com o driver `dummy` do SDL."""

import pygame
import pytest

from politicalizando.conteudo import carregar_textos
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.mapa import Mapa
from politicalizando.dominio.partida import Partida
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.dominio.textos import Textos
from politicalizando.estados.cena import EstadoCena
from politicalizando.estados.mapa import EstadoMapa
from politicalizando.persistencia import carregar

# Cenas e mapa de exemplo, neutros e provisórios: só existem nos testes.
CENAS = Cenas.de_toml(
    """
inicio = "exemplo.sala"

[recusas]
olhar = ["exemplo.recusa"]
usar = ["exemplo.recusa"]
falar = ["exemplo.recusa"]

[[cenas.exemplo.sala.objetos]]
id = "aviso"
nome = "exemplo.aviso"
area = [20, 40, 40, 40]
olhar = [{ marcar_flag = "exemplo.tutorial" }, { fala = "exemplo.recusa" }]

[cenas.exemplo.patio]
entrada = [{ fala = "exemplo.chegada" }]
objetos = [{ id = "banco", nome = "exemplo.banco", area = [20, 40, 40, 40] }]

[cenas.exemplo.porao]
objetos = [{ id = "caixa", nome = "exemplo.caixa", area = [20, 40, 40, 40] }]
"""
)
MAPA = Mapa.de_toml(
    """
se = ["exemplo.tutorial"]

[[locais]]
id = "sala"
nome = "exemplo.mapa.sala"
cena = "exemplo.sala"
area = [20, 60, 80, 30]

[[locais]]
id = "patio"
nome = "exemplo.mapa.patio"
cena = "exemplo.patio"
area = [120, 60, 80, 30]

[[locais]]
id = "porao"
nome = "exemplo.mapa.porao"
cena = "exemplo.porao"
area = [220, 60, 80, 30]
se = ["exemplo.patio.visitou"]
"""
)
TEXTOS = Textos.de_toml(
    "\n".join(
        f'[exemplo.{nome}]\ntexto = "Exemplo {nome}"'
        for nome in ("recusa", "aviso", "chegada", "banco", "caixa")
    )
    + "\n"
    + "\n".join(
        f'[exemplo.mapa.{nome}]\ntexto = "Lugar {nome}"' for nome in ("sala", "patio", "porao")
    )
)


@pytest.fixture
def jogo_exemplo(jogo):
    jogo.textos = Textos({**carregar_textos(), **TEXTOS})
    jogo.interacao = Interacao(CENAS, Roteiros(), Dialogos())
    jogo.mapa = MAPA
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
    """A sala de exemplo, já preparada, ainda sem o mapa liberado."""
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    jogo_exemplo.trocar_estado(tela)
    tela.atualizar(0)
    assert not tela.partida.ocupada
    return tela


def liberar_mapa(cena):
    tecla(cena, pygame.K_1)
    tecla(cena, pygame.K_RETURN)
    assert cena.partida.estado.tem_flag("exemplo.tutorial")


def test_mapa_bloqueado_nao_abre_nem_aparece(cena, jogo_exemplo):
    assert not cena.mapa_liberado
    tecla(cena, pygame.K_m)
    clicar(cena, *cena.botao_mapa.center)
    assert jogo_exemplo.estado is cena
    cena.desenhar(jogo_exemplo.tela)


def test_tecla_m_abre_o_mapa_depois_de_liberado(cena, jogo_exemplo):
    liberar_mapa(cena)
    assert cena.mapa_liberado
    cena.desenhar(jogo_exemplo.tela)
    tecla(cena, pygame.K_m)
    mapa = jogo_exemplo.estado
    assert isinstance(mapa, EstadoMapa)
    assert mapa.foco == "sala", "o foco começa no local atual"
    mapa.desenhar(jogo_exemplo.tela)


def test_botao_mapa_abre_pelo_mouse(cena, jogo_exemplo):
    liberar_mapa(cena)
    clicar(cena, *cena.botao_mapa.center)
    assert isinstance(jogo_exemplo.estado, EstadoMapa)


def test_mapa_nao_abre_durante_uma_fala(cena, jogo_exemplo):
    liberar_mapa(cena)
    tecla(cena, pygame.K_1)
    assert cena.partida.ocupada
    assert not cena.mapa_liberado
    tecla(cena, pygame.K_m)
    assert jogo_exemplo.estado is cena


def test_local_bloqueado_fica_escondido(cena, jogo_exemplo):
    liberar_mapa(cena)
    tecla(cena, pygame.K_m)
    mapa = jogo_exemplo.estado
    assert [local.id for local in mapa._locais()] == ["sala", "patio"]
    clicar(mapa, 260, 75)
    assert jogo_exemplo.estado is mapa, "clicar onde está o local escondido não faz nada"


def test_clique_no_local_leva_a_cena_e_salva_ao_entrar(cena, jogo_exemplo):
    liberar_mapa(cena)
    tecla(cena, pygame.K_m)
    clicar(jogo_exemplo.estado, 160, 75)
    cena.atualizar(0)
    assert jogo_exemplo.estado is cena
    assert cena.partida.cena.id == "exemplo.patio"
    assert cena.caixa.visivel, "a entrada do pátio aparece"
    tecla(cena, pygame.K_RETURN)
    assert carregar().cena_atual == "exemplo.patio"


def test_teclado_no_mapa(cena, jogo_exemplo):
    liberar_mapa(cena)
    tecla(cena, pygame.K_m)
    mapa = jogo_exemplo.estado
    tecla(mapa, pygame.K_TAB)
    assert mapa.foco == "patio"
    tecla(mapa, pygame.K_TAB, mod=pygame.KMOD_LSHIFT)
    assert mapa.foco == "sala"
    tecla(mapa, pygame.K_LEFT)
    assert mapa.foco == "patio", "volta do primeiro para o último"
    tecla(mapa, pygame.K_RETURN)
    assert jogo_exemplo.estado is cena
    assert cena.partida.cena.id == "exemplo.patio"


def test_esc_e_m_voltam_sem_sair_do_lugar(cena, jogo_exemplo):
    liberar_mapa(cena)
    for fechar in (pygame.K_ESCAPE, pygame.K_m):
        tecla(cena, pygame.K_m)
        tecla(jogo_exemplo.estado, fechar)
        assert jogo_exemplo.estado is cena
        assert cena.partida.cena.id == "exemplo.sala"
        assert not cena.partida.ocupada


def test_escolher_o_local_atual_so_fecha_o_mapa(cena, jogo_exemplo):
    liberar_mapa(cena)
    tecla(cena, pygame.K_m)
    tecla(jogo_exemplo.estado, pygame.K_RETURN)
    assert jogo_exemplo.estado is cena
    assert not cena.partida.ocupada


def test_local_liberado_depois_aparece(cena, jogo_exemplo):
    liberar_mapa(cena)
    tecla(cena, pygame.K_m)
    clicar(jogo_exemplo.estado, 160, 75)
    cena.atualizar(0)
    tecla(cena, pygame.K_RETURN)
    tecla(cena, pygame.K_m)
    mapa = jogo_exemplo.estado
    assert [local.id for local in mapa._locais()] == ["sala", "patio", "porao"]
    mapa.desenhar(jogo_exemplo.tela)
