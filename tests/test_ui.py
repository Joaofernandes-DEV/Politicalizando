"""Componentes de interface: quebra de linhas, caixa de diálogo e menu de verbos."""

import pygame
import pytest

from politicalizando.config import ALTURA_TELA, LARGURA_TELA
from politicalizando.conteudo import carregar_dialogos, carregar_textos
from politicalizando.dominio.acoes import Escolha, Esperar, Fala
from politicalizando.dominio.cenas import Area, Verbo
from politicalizando.dominio.checagem import ORDEM_DAS_CLASSES
from politicalizando.ui.caixa_dialogo import CONFIRMAR, MAXIMO_DE_LINHAS, CaixaDialogo
from politicalizando.ui.menu_verbos import FECHAR, MenuVerbos
from politicalizando.ui.texto import criar_fonte, quebrar_linhas


@pytest.fixture
def fonte():
    pygame.font.init()
    yield criar_fonte()
    pygame.font.quit()


@pytest.fixture
def textos():
    return carregar_textos()


def tecla(key):
    return pygame.Event(pygame.KEYDOWN, key=key, mod=0)


# --- Quebra de linhas -----------------------------------------------------------------------


def test_quebra_sem_cortar_palavras_e_respeita_a_largura(fonte):
    texto = "Uma frase comprida o bastante para ocupar mais de uma linha na caixa de diálogo."
    linhas = quebrar_linhas(fonte, texto, 120)
    assert len(linhas) > 1
    assert " ".join(linhas) == texto
    assert all(fonte.size(linha)[0] <= 120 for linha in linhas)


def test_quebra_respeita_as_quebras_do_texto(fonte):
    assert quebrar_linhas(fonte, "Um.\nDois.", 300) == ["Um.", "Dois."]


def test_palavra_maior_que_a_largura_fica_sozinha(fonte):
    assert quebrar_linhas(fonte, "a palavrapalavrapalavra b", 20) == [
        "a",
        "palavrapalavrapalavra",
        "b",
    ]


# --- Todo texto cabe na tela ----------------------------------------------------------------


def test_todo_texto_do_jogo_cabe_na_caixa(fonte, textos):
    caixa = CaixaDialogo(fonte, textos)
    longos = [
        id_texto for id_texto in textos if len(caixa.linhas_da_fala(id_texto)) > MAXIMO_DE_LINHAS
    ]
    assert longos == []


def test_toda_opcao_cabe_numa_linha(fonte, textos):
    opcoes = {
        opcao.texto
        for dialogo in carregar_dialogos().values()
        for no in dialogo.nos.values()
        for opcao in no.opcoes
    }
    opcoes |= {f"checagem.classe.{classe}" for classe in ORDEM_DAS_CLASSES}
    caixa = CaixaDialogo(fonte, textos)
    longas = [
        id_texto
        for id_texto in sorted(opcoes)
        if fonte.size(f"9. {textos[id_texto].texto}")[0] > caixa.largura_texto
    ]
    assert longas == []


# --- Caixa de diálogo -----------------------------------------------------------------------


def test_fala_avanca_com_clique_enter_e_espaco(fonte, textos):
    caixa = CaixaDialogo(fonte, textos)
    caixa.mostrar(Fala("titulo.frase"))
    assert caixa.visivel
    assert caixa.retangulo.bottom <= ALTURA_TELA
    clique = pygame.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=1)
    for evento in (clique, tecla(pygame.K_RETURN), tecla(pygame.K_SPACE)):
        assert caixa.tratar_evento(evento) == CONFIRMAR
    assert caixa.tratar_evento(tecla(pygame.K_a)) is None
    clique_direito = pygame.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=3)
    assert caixa.tratar_evento(clique_direito) is None


def test_escolha_por_numero_so_aceita_opcoes_que_existem(fonte, textos):
    caixa = CaixaDialogo(fonte, textos)
    caixa.mostrar(Escolha(("checagem.classe.fato", "checagem.classe.opiniao")))
    assert caixa.tratar_evento(tecla(pygame.K_3)) is None
    assert caixa.tratar_evento(tecla(pygame.K_2)) == 1
    assert caixa.tratar_evento(tecla(pygame.K_UP)) is None
    assert caixa.tratar_evento(tecla(pygame.K_RETURN)) == 1, "a seta para cima dá a volta"


def test_esperar_nao_mostra_a_caixa(fonte, textos):
    caixa = CaixaDialogo(fonte, textos)
    caixa.mostrar(Esperar(1))
    assert not caixa.visivel
    assert caixa.tratar_evento(tecla(pygame.K_RETURN)) is None


def test_nova_escolha_volta_a_selecao_para_a_primeira(fonte, textos):
    caixa = CaixaDialogo(fonte, textos)
    caixa.mostrar(Escolha(("checagem.classe.fato", "checagem.classe.opiniao")))
    caixa.tratar_evento(tecla(pygame.K_DOWN))
    caixa.mostrar(Escolha(("checagem.classe.opiniao", "checagem.classe.manipulacao")))
    assert caixa.tratar_evento(tecla(pygame.K_RETURN)) == 0


# --- Menu de verbos -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "area",
    [Area(10, 10, 20, 20), Area(300, 10, 20, 20), Area(0, 170, 320, 10), Area(0, 0, 320, 180)],
    ids=["meio", "borda-direita", "embaixo", "tela-inteira"],
)
def test_menu_abre_sempre_dentro_da_tela(fonte, textos, area):
    menu = MenuVerbos(fonte, textos)
    menu.abrir(area)
    tela = pygame.Rect(0, 0, LARGURA_TELA, ALTURA_TELA)
    assert all(tela.contains(botao) for botao in menu.botoes)


def test_menu_abre_ao_lado_do_objeto(fonte, textos):
    menu = MenuVerbos(fonte, textos)
    menu.abrir(Area(10, 10, 20, 20))
    assert menu.botoes[0].left > 30
    menu.abrir(Area(280, 10, 30, 20))
    assert menu.botoes[0].right < 280


def test_menu_responde_a_numeros_setas_e_esc(fonte, textos):
    menu = MenuVerbos(fonte, textos)
    menu.abrir(Area(10, 10, 20, 20))
    assert menu.tratar_evento(tecla(pygame.K_3)) == Verbo.FALAR
    assert not menu.aberto
    menu.abrir(Area(10, 10, 20, 20))
    menu.tratar_evento(tecla(pygame.K_UP))
    assert menu.tratar_evento(tecla(pygame.K_RETURN)) == Verbo.FALAR
    menu.abrir(Area(10, 10, 20, 20))
    assert menu.tratar_evento(tecla(pygame.K_4)) is None
    assert menu.tratar_evento(tecla(pygame.K_ESCAPE)) == FECHAR
    assert not menu.aberto
    assert menu.tratar_evento(tecla(pygame.K_1)) is None, "fechado, o menu não responde"
