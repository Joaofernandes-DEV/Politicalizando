"""Tela da matéria, aberta por `abrir_tela`, com o driver `dummy` do SDL."""

import pygame
import pytest

from politicalizando.conteudo import carregar_textos
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.materia import FLAG_PUBLICOU, Inclusao, Nivel, Pecas
from politicalizando.dominio.partida import Partida
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.dominio.textos import Textos
from politicalizando.estados.cena import EstadoCena
from politicalizando.estados.materia import CITAR, COMENTARIO, INCLUIR, LISTA, EstadoMateria

# Cena e peças de exemplo, neutras e provisórias: só existem nos testes.
CENAS = Cenas.de_toml(
    """
inicio = "exemplo.sala"

[recusas]
olhar = ["exemplo.recusa"]
usar = ["exemplo.recusa"]
falar = ["exemplo.recusa"]

[[cenas.exemplo.sala.objetos]]
id = "maquina"
nome = "exemplo.maquina"
area = [20, 40, 40, 40]
usar = [{ abrir_tela = "materia" }]
olhar = [{ marcar_flag = "exemplo.leu_fonte" }, { fala = "exemplo.recusa" }]
"""
)
PECAS = Pecas.de_toml(
    """
[pecas.exemplo.fato]
tipo = "fato"
texto = "exemplo.fato"
fonte_se = ["exemplo.leu_fonte"]

[pecas.exemplo.opiniao]
tipo = "opiniao"
texto = "exemplo.opiniao"
de = "exemplo.pessoa"

[pecas.exemplo.boato]
tipo = "manipulacao"
texto = "exemplo.boato"
"""
)
TEXTOS = Textos.de_toml(
    "\n".join(
        f'[exemplo.{nome}]\ntexto = "Exemplo {nome}."'
        for nome in ("recusa", "maquina", "fato", "opiniao", "boato")
    )
)


@pytest.fixture
def jogo_exemplo(jogo):
    jogo.textos = Textos({**carregar_textos(), **TEXTOS})
    jogo.interacao = Interacao(CENAS, Roteiros(), Dialogos())
    jogo.pecas = PECAS
    return jogo


def tecla(tela, key):
    tela.tratar_evento(pygame.Event(pygame.KEYDOWN, key=key, mod=0))
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


def abrir(cena, ler_fonte: bool = False) -> EstadoMateria:
    if ler_fonte:
        tecla(cena, pygame.K_TAB)
        tecla(cena, pygame.K_1)
        tecla(cena, pygame.K_RETURN)
    tecla(cena, pygame.K_TAB)
    tecla(cena, pygame.K_2)
    tela = cena.jogo.estado
    assert isinstance(tela, EstadoMateria)
    return tela


def textos(tela) -> list[str]:
    return [linha.texto for linha in tela.linhas()]


def test_lista_as_pecas_sem_mostrar_o_tipo(cena, jogo_exemplo):
    tela = abrir(cena)
    linhas = textos(tela)
    for nome in ("fato", "opiniao", "boato"):
        assert f"Exemplo {nome}." in linhas
    assert not any("manipula" in linha.lower() for linha in linhas)
    sem_fonte = f"({jogo_exemplo.textos['materia.sem_fonte'].texto})"
    assert linhas.count(sem_fonte) == 2, "o fato sem fonte conferida e o boato parecem iguais"
    assert jogo_exemplo.textos["materia.citar_quem"].texto in linhas
    tela.desenhar(jogo_exemplo.tela)


def test_incluir_e_citar_pelo_teclado(cena):
    tela = abrir(cena, ler_fonte=True)
    tecla(tela, pygame.K_RETURN)
    assert tela.inclusoes() == [Inclusao("exemplo.fato")]
    tecla(tela, pygame.K_RIGHT)
    tecla(tela, pygame.K_SPACE)
    assert tela.inclusoes() == [Inclusao("exemplo.fato", citar=True)]
    tecla(tela, pygame.K_DOWN)
    tecla(tela, pygame.K_RETURN)
    assert tela.inclusoes()[1] == Inclusao("exemplo.opiniao", citar=True), "citar já inclui"
    tecla(tela, pygame.K_LEFT)
    tecla(tela, pygame.K_RETURN)
    assert [i.peca for i in tela.inclusoes()] == ["exemplo.fato"], "tirar a peça tira a citação"


def test_citar_bloqueado_sem_fonte_conferida(cena):
    tela = abrir(cena)
    tela.alternar(0, CITAR)
    tela.alternar(2, CITAR)
    assert tela.inclusoes() == []


def test_clique_nas_caixas(cena, jogo_exemplo):
    tela = abrir(cena)
    linhas = tela.linhas()
    indice = next(
        i for i, linha in enumerate(linhas) if linha.peca == 1 and linha.coluna == INCLUIR
    )
    clicar(tela, tela.area.x + 20, tela.area.y + indice * tela.altura_linha + 2)
    assert tela.inclusoes() == [Inclusao("exemplo.opiniao")]
    assert (tela.selecionada, tela.coluna) == (1, INCLUIR)


def test_entregar_mostra_o_comentario_e_reescrever_mantem_as_escolhas(cena, jogo_exemplo):
    tela = abrir(cena, ler_fonte=True)
    tela.alternar(0, CITAR)
    tela.alternar(1, CITAR)
    tecla(tela, pygame.K_e)
    assert tela.modo == COMENTARIO
    assert (tela.avaliacao.fatos, tela.avaliacao.atribuicao) == (Nivel.BEM_FEITO, Nivel.BEM_FEITO)
    linhas = " ".join(textos(tela))
    assert jogo_exemplo.textos["materia.explica.fatos.bem_feito"].texto in linhas
    assert jogo_exemplo.textos["materia.explica.justica.precisa_melhorar"].texto in linhas
    tela.desenhar(jogo_exemplo.tela)
    assert not cena.partida.estado.tem_flag(FLAG_PUBLICOU), "entregar não publica"

    tecla(tela, pygame.K_r)
    assert tela.modo == LISTA
    assert len(tela.inclusoes()) == 2


def test_boato_incluido_pesa_nos_fatos(cena):
    tela = abrir(cena, ler_fonte=True)
    tela.alternar(0, CITAR)
    tela.alternar(2, INCLUIR)
    tela.entregar()
    assert tela.avaliacao.fatos is Nivel.EM_PARTE


def test_publicar_marca_a_flag_e_volta_para_a_cena(cena, jogo_exemplo):
    tela = abrir(cena)
    tecla(tela, pygame.K_e)
    tecla(tela, pygame.K_p)
    assert cena.partida.estado.tem_flag(FLAG_PUBLICOU)
    assert jogo_exemplo.estado is cena
    cena.atualizar(0)
    assert not cena.partida.ocupada


def test_botoes_pelo_mouse(cena, jogo_exemplo):
    tela = abrir(cena)
    clicar(tela, *tela.botao_entregar[0].center)
    assert tela.modo == COMENTARIO
    clicar(tela, *tela.botao_reescrever[0].center)
    assert tela.modo == LISTA
    clicar(tela, *tela.botao_entregar[0].center)
    clicar(tela, *tela.botao_publicar[0].center)
    assert jogo_exemplo.estado is cena


def test_esc_sai_sem_entregar(cena, jogo_exemplo):
    tela = abrir(cena)
    tela.alternar(1, INCLUIR)
    tecla(tela, pygame.K_ESCAPE)
    assert jogo_exemplo.estado is cena
    assert not cena.partida.estado.tem_flag(FLAG_PUBLICOU)


def test_sem_pecas_mostra_o_aviso(cena, jogo_exemplo):
    jogo_exemplo.pecas = Pecas()
    tela = abrir(cena)
    vazio = jogo_exemplo.textos["materia.vazio"].texto
    assert " ".join(textos(tela)) == vazio
    tecla(tela, pygame.K_DOWN)
    tecla(tela, pygame.K_e)
    assert tela.avaliacao.total == 0
    tela.desenhar(jogo_exemplo.tela)


def test_maquina_do_jogo_real_abre(jogo):
    tela = EstadoCena(jogo, Partida.nova(jogo.interacao))
    jogo.trocar_estado(tela)
    tela.atualizar(0)
    tela.partida.confirmar()
    tela.atualizar(0)
    tela.partida.confirmar()
    tela.atualizar(0)
    maquina = next(objeto for objeto in tela.partida.objetos() if objeto.id == "maquina")
    tela.partida.agir(maquina, "usar")
    tela.atualizar(0)
    materia = jogo.estado
    assert isinstance(materia, EstadoMateria)
    materia.desenhar(jogo.tela)
    tecla(materia, pygame.K_ESCAPE)
    assert jogo.estado is tela
