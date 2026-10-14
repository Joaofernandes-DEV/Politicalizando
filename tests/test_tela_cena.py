"""Tela de cena e tela de título com o driver `dummy` do SDL: input, bloqueio, save e Esc."""

import pygame
import pytest

from politicalizando.conteudo import carregar_textos
from politicalizando.dominio.acoes import Escolha, Fala
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.partida import Partida
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.dominio.textos import Textos
from politicalizando.estados import cena as tela_cena
from politicalizando.estados.cena import EstadoCena
from politicalizando.estados.titulo import EstadoTitulo
from politicalizando.persistencia import caminho_save, carregar, existe_save, salvar

# Cena de exemplo, neutra e provisória: só existe nos testes.
CENAS = Cenas.de_toml(
    """
inicio = "exemplo.sala"

[recusas]
olhar = ["exemplo.recusa"]
usar = ["exemplo.recusa"]
falar = ["exemplo.recusa"]

[cenas.exemplo.sala]
entrada = [{ fala = "exemplo.ola" }]

[[cenas.exemplo.sala.objetos]]
id = "caixa"
nome = "exemplo.caixa.nome"
area = [20, 20, 40, 40]
olhar = [{ fala = "exemplo.caixa.olhar" }]
usar = [{ dar_item = "caixa" }]
se_nao_item = ["caixa"]

[[cenas.exemplo.sala.objetos]]
id = "guia"
nome = "exemplo.guia"
area = [100, 20, 40, 80]
falar = { dialogo = "exemplo.guia" }

[[cenas.exemplo.sala.objetos]]
id = "porta"
nome = "exemplo.porta"
area = [280, 20, 30, 100]
usar = [{ trocar_cena = "exemplo.corredor" }]

[cenas.exemplo.corredor]
[[cenas.exemplo.corredor.objetos]]
id = "volta"
nome = "exemplo.volta"
area = [10, 20, 30, 100]
usar = [{ trocar_cena = "exemplo.sala" }]
"""
)
DIALOGOS = Dialogos.de_toml(
    """
[exemplo.guia]
inicio = "a"
[exemplo.guia.nos.a]
opcoes = [
  { id = "sim", texto = "exemplo.sim", vai_para = "fim" },
  { id = "nao", texto = "exemplo.nao", vai_para = "fim" },
]
"""
)
TEXTOS = Textos.de_toml(
    "\n".join(
        f'[exemplo.{nome}]\ntexto = "Exemplo {nome}"'
        for nome in ("recusa", "ola", "guia", "porta", "volta", "sim", "nao")
    )
    + '\n[exemplo.caixa.nome]\ntexto = "Caixa"\n[exemplo.caixa.olhar]\ntexto = "Uma caixa."'
)


@pytest.fixture
def jogo_exemplo(jogo):
    jogo.textos = Textos({**carregar_textos(), **TEXTOS})
    jogo.interacao = Interacao(CENAS, Roteiros(), DIALOGOS)
    return jogo


def tecla(tela, key, mod=0):
    tela.tratar_evento(pygame.Event(pygame.KEYDOWN, key=key, mod=mod))
    tela.atualizar(0)


def clicar(tela, x, y):
    tela.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=(x, y)))
    tela.tratar_evento(pygame.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1))
    tela.atualizar(0)


def desenha_sem_erro(tela, jogo):
    tela.desenhar(jogo.tela)


@pytest.fixture
def tela(jogo_exemplo):
    """A cena de exemplo num jogo novo, já com a fala de boas-vindas confirmada."""
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    tela.atualizar(0)
    tecla(tela, pygame.K_RETURN)
    assert not tela.partida.ocupada
    return tela


def acao(tela):
    return tela.partida.diretor.acao_atual


# --- Entrada e autosave ---------------------------------------------------------------------


def test_jogo_novo_mostra_a_entrada_e_bloqueia_o_clique(jogo_exemplo):
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    tela.atualizar(0)
    assert acao(tela) == Fala("exemplo.ola")
    assert tela.caixa.visivel
    desenha_sem_erro(tela, jogo_exemplo)

    clicar(tela, 30, 30)
    assert not tela.menu.aberto, "durante a fala, o clique só avança a caixa"
    assert acao(tela) is None
    assert not tela.partida.ocupada


def test_autosave_quando_a_entrada_termina(jogo_exemplo):
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    tela.atualizar(0)
    assert not existe_save(), "a entrada ainda está rodando"
    tecla(tela, pygame.K_SPACE)
    salvo = carregar()
    assert salvo.cena_atual == "exemplo.sala"
    assert salvo.tem_flag("exemplo.sala.visitou")


def test_save_que_falha_vira_um_aviso_na_caixa(jogo_exemplo, monkeypatch):
    def falha(*_, **__):
        raise PermissionError("pasta sem permissão")

    monkeypatch.setattr(tela_cena, "autosalvar", falha)
    tela = EstadoCena(jogo_exemplo, Partida.nova(jogo_exemplo.interacao))
    tela.atualizar(0)
    tecla(tela, pygame.K_RETURN)
    assert acao(tela) == Fala("aviso.save_falhou")
    tecla(tela, pygame.K_RETURN)
    assert not tela.partida.ocupada


# --- Mouse ----------------------------------------------------------------------------------


def test_passar_o_mouse_destaca_e_mostra_o_nome(tela, jogo_exemplo):
    tela.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=(30, 30)))
    assert tela.sob_mouse == "caixa"
    desenha_sem_erro(tela, jogo_exemplo)
    tela.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=(200, 170)))
    assert tela.sob_mouse is None


def test_clique_abre_o_menu_e_o_verbo_roda(tela, jogo_exemplo):
    clicar(tela, 30, 30)
    assert tela.menu.aberto
    assert tela.foco == "caixa"
    desenha_sem_erro(tela, jogo_exemplo)

    olhar = tela.menu.botoes[0]
    clicar(tela, *olhar.center)
    assert not tela.menu.aberto
    assert acao(tela) == Fala("exemplo.caixa.olhar")
    desenha_sem_erro(tela, jogo_exemplo)


def test_clique_fora_fecha_o_menu(tela):
    clicar(tela, 30, 30)
    clicar(tela, 200, 170)
    assert not tela.menu.aberto
    assert not tela.partida.ocupada


def test_clique_no_vazio_nao_faz_nada(tela):
    clicar(tela, 200, 170)
    assert not tela.menu.aberto
    assert tela.foco is None


def test_escolha_pelo_mouse(tela, jogo_exemplo):
    clicar(tela, 110, 40)
    clicar(tela, *tela.menu.botoes[2].center)
    assert acao(tela) == Escolha(("exemplo.sim", "exemplo.nao"))
    desenha_sem_erro(tela, jogo_exemplo)

    caixa = tela.caixa.retangulo
    segunda = (caixa.x + 20, caixa.y + 4 + tela.caixa.altura_linha + 2)
    clicar(tela, *segunda)
    assert tela.partida.estado.tem_flag("exemplo.guia.nao")


# --- Teclado --------------------------------------------------------------------------------


def test_tab_e_setas_percorrem_os_objetos(tela):
    tecla(tela, pygame.K_TAB)
    assert tela.foco == "caixa"
    tecla(tela, pygame.K_TAB)
    assert tela.foco == "guia"
    tecla(tela, pygame.K_TAB, mod=pygame.KMOD_LSHIFT)
    assert tela.foco == "caixa"
    tecla(tela, pygame.K_LEFT)
    assert tela.foco == "porta", "volta do primeiro para o último"
    tecla(tela, pygame.K_DOWN)
    assert tela.foco == "caixa"


def test_enter_abre_o_menu_e_os_numeros_escolhem_o_verbo(tela):
    tecla(tela, pygame.K_RETURN)
    assert tela.foco == "caixa", "sem foco, o Enter vai para o primeiro objeto"
    assert tela.menu.aberto
    tecla(tela, pygame.K_2)
    assert not tela.menu.aberto
    assert tela.partida.estado.tem_item("caixa")
    assert tela.foco is None, "o objeto coletado sumiu e levou o foco"


def test_numero_usa_o_verbo_direto_no_objeto_em_foco(tela):
    tecla(tela, pygame.K_TAB)
    tecla(tela, pygame.K_1)
    assert acao(tela) == Fala("exemplo.caixa.olhar")
    tecla(tela, pygame.K_RETURN)
    tecla(tela, pygame.K_KP3)
    assert acao(tela) == Fala("exemplo.recusa")


def test_menu_pelo_teclado(tela):
    tecla(tela, pygame.K_TAB)
    tecla(tela, pygame.K_SPACE)
    tecla(tela, pygame.K_DOWN)
    tecla(tela, pygame.K_RETURN)
    assert tela.partida.estado.tem_item("caixa")


def test_escolha_pelo_teclado(tela):
    tecla(tela, pygame.K_TAB)
    tecla(tela, pygame.K_TAB)
    tecla(tela, pygame.K_3)
    tecla(tela, pygame.K_DOWN)
    tecla(tela, pygame.K_RETURN)
    assert tela.partida.estado.tem_flag("exemplo.guia.nao")
    assert not tela.partida.ocupada


def test_input_bloqueado_durante_a_fala(tela):
    tecla(tela, pygame.K_TAB)
    tecla(tela, pygame.K_1)
    tecla(tela, pygame.K_TAB)
    assert tela.foco == "caixa", "o Tab não mexe no foco enquanto a fala espera"
    tela.jogo.trocar_estado(tela)
    tecla(tela, pygame.K_ESCAPE)
    assert tela.jogo.estado is tela
    assert acao(tela) == Fala("exemplo.caixa.olhar"), "o Esc não sai no meio de uma fala"


def test_trocar_de_cena_limpa_o_foco(tela):
    tecla(tela, pygame.K_LEFT)
    assert tela.foco == "porta"
    tecla(tela, pygame.K_2)
    assert tela.partida.cena.id == "exemplo.corredor"
    assert tela.foco is None
    assert carregar().cena_atual == "exemplo.corredor"


# --- Esc e título ---------------------------------------------------------------------------


def test_esc_fecha_o_menu_e_depois_volta_ao_titulo_salvando(tela, jogo_exemplo):
    jogo_exemplo.trocar_estado(tela)
    tecla(tela, pygame.K_RETURN)
    tecla(tela, pygame.K_2)
    assert tela.partida.estado.tem_item("caixa")

    tecla(tela, pygame.K_RETURN)
    tecla(tela, pygame.K_ESCAPE)
    assert not tela.menu.aberto
    assert jogo_exemplo.estado is tela

    tecla(tela, pygame.K_ESCAPE)
    assert isinstance(jogo_exemplo.estado, EstadoTitulo)
    assert carregar().tem_item("caixa")


def test_esc_com_save_falhando_volta_ao_titulo_com_aviso(tela, jogo_exemplo, monkeypatch):
    def falha(*_, **__):
        raise PermissionError("pasta sem permissão")

    monkeypatch.setattr(tela_cena, "autosalvar", falha)
    jogo_exemplo.trocar_estado(tela)
    tecla(tela, pygame.K_ESCAPE)
    titulo = jogo_exemplo.estado
    assert isinstance(titulo, EstadoTitulo)
    assert titulo.aviso == jogo_exemplo.textos["aviso.save_falhou"].texto
    titulo.desenhar(jogo_exemplo.tela)


def test_titulo_sem_save_so_oferece_novo_jogo(jogo_exemplo):
    titulo = EstadoTitulo(jogo_exemplo)
    assert [rotulo for rotulo, _ in titulo.opcoes] == ["Novo jogo"]
    jogo_exemplo.trocar_estado(titulo)
    tecla(titulo, pygame.K_RETURN)
    assert isinstance(jogo_exemplo.estado, EstadoCena)
    assert jogo_exemplo.estado.partida.estado.cena_atual == "exemplo.sala"


def test_titulo_continuar_volta_para_a_cena_salva(jogo_exemplo):
    estado = EstadoJogo()
    estado.entrar_na_cena("exemplo.corredor")
    estado.marcar_flag("exemplo.corredor.visitou")
    salvar(estado)

    titulo = EstadoTitulo(jogo_exemplo)
    assert [rotulo for rotulo, _ in titulo.opcoes] == ["Novo jogo", "Continuar"]
    jogo_exemplo.trocar_estado(titulo)
    titulo.desenhar(jogo_exemplo.tela)
    tecla(titulo, pygame.K_DOWN)
    tecla(titulo, pygame.K_RETURN)
    tela = jogo_exemplo.estado
    assert isinstance(tela, EstadoCena)
    tela.atualizar(0)
    assert tela.partida.cena.id == "exemplo.corredor"
    assert not tela.partida.ocupada


def test_titulo_pelo_mouse(jogo_exemplo):
    titulo = EstadoTitulo(jogo_exemplo)
    jogo_exemplo.trocar_estado(titulo)
    clicar(titulo, *titulo._botoes[0].center)
    assert isinstance(jogo_exemplo.estado, EstadoCena)


@pytest.mark.parametrize(
    "conteudo",
    [
        "{ quebrado",
        '{"versao": 1, "cena_atual": "exemplo.sumiu", "flags": [], "inventario": []}',
    ],
    ids=["ilegivel", "cena-que-nao-existe"],
)
def test_titulo_com_save_invalido_avisa_e_mantem_o_arquivo(jogo_exemplo, conteudo):
    caminho = caminho_save()
    caminho.parent.mkdir(parents=True)
    caminho.write_text(conteudo, encoding="utf-8")

    titulo = EstadoTitulo(jogo_exemplo)
    jogo_exemplo.trocar_estado(titulo)
    tecla(titulo, pygame.K_DOWN)
    tecla(titulo, pygame.K_RETURN)
    assert jogo_exemplo.estado is titulo
    assert titulo.aviso == jogo_exemplo.textos["titulo.save_invalido"].texto
    titulo.desenhar(jogo_exemplo.tela)
    assert caminho.read_text(encoding="utf-8") == conteudo


def test_jogo_real_abre_a_cena_inicial(jogo):
    titulo = EstadoTitulo(jogo)
    jogo.trocar_estado(titulo)
    tecla(titulo, pygame.K_RETURN)
    tela = jogo.estado
    tela.atualizar(0)
    tela.desenhar(jogo.tela)
    assert tela.partida.cena.id == jogo.interacao.cenas.inicio
