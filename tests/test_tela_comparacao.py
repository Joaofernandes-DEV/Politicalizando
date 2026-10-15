"""Tela de comparação de propostas, aberta por `abrir_tela`, com o driver `dummy` do SDL."""

import pygame
import pytest

from politicalizando.conteudo import carregar_textos
from politicalizando.dominio.acoes import AbrirTela, Fala
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.partida import Partida
from politicalizando.dominio.propostas import FLAG_COMPAROU, Propostas
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.dominio.textos import Textos
from politicalizando.estados.cena import EstadoCena
from politicalizando.estados.comparacao import EstadoComparacao

# Cena e propostas de exemplo, neutras e provisórias: só existem nos testes.
CENAS = Cenas.de_toml(
    """
inicio = "exemplo.sala"

[recusas]
olhar = ["exemplo.recusa"]
usar = ["exemplo.recusa"]
falar = ["exemplo.recusa"]

[[cenas.exemplo.sala.objetos]]
id = "quadro"
nome = "exemplo.quadro"
area = [20, 40, 40, 40]
usar = [{ abrir_tela = "comparacao" }, { fala = "exemplo.depois" }]
olhar = [{ marcar_flag = "exemplo.ouviu_a" }, { marcar_flag = "exemplo.ouviu_b" }]
"""
)


def _proposta(corrente: str, flag: str) -> str:
    return (
        f'[propostas.{corrente}]\nse = ["{flag}"]\nproposta = "exemplo.{corrente}.proposta"\n'
        f'pros = ["exemplo.item"]\ncontras = ["exemplo.item"]\nvalores = ["exemplo.item"]\n'
    )


PROPOSTAS = Propostas.de_toml(
    _proposta("socialismo", "exemplo.ouviu_a") + _proposta("conservadorismo", "exemplo.ouviu_b")
)
TEXTOS = Textos.de_toml(
    "\n".join(
        f'[exemplo.{nome}]\ntexto = "Exemplo {nome}"' for nome in ("recusa", "quadro", "depois")
    )
    + '\n[exemplo.item]\ntexto = "Um item de exemplo."\n'
    + "".join(
        f'[exemplo.{c}.proposta]\ntexto = "{"Uma proposta de exemplo bem comprida. " * 8}"\n'
        for c in ("socialismo", "conservadorismo")
    )
)


@pytest.fixture
def jogo_exemplo(jogo):
    jogo.textos = Textos({**carregar_textos(), **TEXTOS})
    jogo.interacao = Interacao(CENAS, Roteiros(), Dialogos())
    jogo.propostas = PROPOSTAS
    return jogo


def tecla(tela, key, mod=0):
    tela.tratar_evento(pygame.Event(pygame.KEYDOWN, key=key, mod=mod))
    tela.atualizar(0)


def clicar(tela, x, y):
    tela.tratar_evento(pygame.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1))
    tela.atualizar(0)


@pytest.fixture
def cena(jogo_exemplo):
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    jogo_exemplo.trocar_estado(tela)
    tela.atualizar(0)
    return tela


def abrir_quadro(cena) -> EstadoComparacao:
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_2)
    tela = cena.jogo.estado
    assert isinstance(tela, EstadoComparacao)
    assert cena.partida.diretor.acao_atual == AbrirTela("comparacao")
    return tela


def test_sem_propostas_ouvidas_mostra_o_aviso_e_nao_marca_a_flag(cena, jogo_exemplo):
    tela = abrir_quadro(cena)
    assert tela.propostas == ()
    vazio = jogo_exemplo.textos["comparacao.vazio"].texto
    assert " ".join(texto for texto, _ in tela.linhas()) == vazio
    assert not cena.partida.estado.tem_flag(FLAG_COMPAROU)
    tela.desenhar(jogo_exemplo.tela)


def test_fechar_a_tela_devolve_a_cena_e_o_roteiro_continua(cena, jogo_exemplo):
    tela = abrir_quadro(cena)
    tecla(tela, pygame.K_ESCAPE)
    assert jogo_exemplo.estado is cena
    cena.atualizar(0)
    assert cena.partida.diretor.acao_atual == Fala("exemplo.depois")
    assert cena.caixa.visivel
    tecla(cena, pygame.K_RETURN)
    assert not cena.partida.ocupada


def test_propostas_na_ordem_fixa_e_flag_de_comparou(cena, jogo_exemplo):
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_1)
    tela = abrir_quadro(cena)
    assert [p.corrente for p in tela.propostas] == ["conservadorismo", "socialismo"]
    assert cena.partida.estado.tem_flag(FLAG_COMPAROU)
    nome = jogo_exemplo.textos["corrente.conservadorismo"].texto
    assert tela.cabecalho() == f"{nome} (1 de 2)"
    linhas = [texto for texto, _ in tela.linhas()]
    for secao in ("comparacao.proposta", "comparacao.pros", "comparacao.contras"):
        assert jogo_exemplo.textos[secao].texto in linhas
    assert "- Um item de exemplo." in linhas
    tela.desenhar(jogo_exemplo.tela)


def test_trocar_e_rolar(cena, jogo_exemplo):
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_1)
    tela = abrir_quadro(cena)
    tecla(tela, pygame.K_RIGHT)
    assert tela.propostas[tela.atual].corrente == "socialismo"
    tecla(tela, pygame.K_RIGHT)
    assert tela.atual == 0, "dá a volta"
    clicar(tela, *tela.seta_anterior.center)
    assert tela.atual == 1
    clicar(tela, *tela.seta_proxima.center)
    assert tela.atual == 0

    total = len(tela.linhas())
    assert total > tela.linhas_visiveis
    tecla(tela, pygame.K_DOWN)
    assert tela.rolagem == 1
    tecla(tela, pygame.K_PAGEDOWN)
    tela.tratar_evento(pygame.Event(pygame.MOUSEWHEEL, x=0, y=-100))
    assert tela.rolagem == total - tela.linhas_visiveis
    tela.desenhar(jogo_exemplo.tela)
    tecla(tela, pygame.K_LEFT)
    assert tela.rolagem == 0, "trocar de proposta volta ao topo"


def test_quadro_do_jogo_real_abre_e_fecha(jogo):
    from politicalizando.dominio.estado_jogo import EstadoJogo

    estado = EstadoJogo()
    estado.entrar_na_cena("teste.corredor")
    partida = Partida(estado, jogo.interacao)
    tela = EstadoCena(jogo, partida)
    jogo.trocar_estado(tela)
    tela.atualizar(0)
    quadro = next(objeto for objeto in partida.objetos() if objeto.id == "quadro")
    partida.agir(quadro, "usar")
    tela.atualizar(0)
    comparacao = jogo.estado
    assert isinstance(comparacao, EstadoComparacao)
    comparacao.desenhar(jogo.tela)
    tecla(comparacao, pygame.K_ESCAPE)
    assert jogo.estado is tela
