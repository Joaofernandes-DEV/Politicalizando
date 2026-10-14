import pytest

from politicalizando.dominio.acoes import Escolha, Esperar, Fala
from politicalizando.dominio.cenas import Cenas, Verbo
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.estado_jogo import EstadoJogo, SaveInvalido
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.partida import Partida
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.persistencia import autosalvar, carregar, existe_save

# Cenas, roteiros e diálogo de exemplo, neutros e provisórios: só existem nos testes.
CENAS = """
inicio = "exemplo.sala"

[recusas]
olhar = ["exemplo.recusa.olhar"]
usar = ["exemplo.recusa.usar"]
falar = ["exemplo.recusa.falar"]

[cenas.exemplo.sala]
entrada = { roteiro = "exemplo.chegada" }

[[cenas.exemplo.sala.objetos]]
id = "folheto"
nome = "exemplo.folheto.nome"
area = [40, 100, 16, 12]
olhar = [{ fala = "exemplo.folheto.olhar" }]
usar = [{ dar_item = "folheto" }]
se_nao_item = ["folheto"]

[[cenas.exemplo.sala.objetos]]
id = "porta"
nome = "exemplo.porta.nome"
area = [280, 40, 30, 90]
usar = [{ fala = "exemplo.porta.abre" }, { trocar_cena = "exemplo.corredor" }, { fala = "x.y" }]

[[cenas.exemplo.sala.objetos]]
id = "relogio"
nome = "exemplo.relogio.nome"
area = [40, 20, 20, 20]
usar = [{ esperar = 1 }, { fala = "exemplo.relogio.tique" }]

[[cenas.exemplo.sala.objetos]]
id = "guia"
nome = "exemplo.guia.nome"
area = [200, 60, 24, 60]
falar = { dialogo = "exemplo.guia" }

[cenas.exemplo.corredor]
entrada = [{ fala = "exemplo.corredor.chegada" }]

[[cenas.exemplo.corredor.objetos]]
id = "volta"
nome = "exemplo.volta.nome"
area = [10, 40, 30, 90]
usar = [{ trocar_cena = "exemplo.sala" }]
"""

ROTEIROS = Roteiros.de_toml('exemplo.chegada = [{ fala = "exemplo.chegada.ola" }]')
DIALOGOS = Dialogos.de_toml(
    """
[exemplo.guia]
inicio = "a"
[exemplo.guia.nos.a]
passos = [{ fala = "exemplo.guia.ola" }]
opcoes = [
  { id = "pergunta", texto = "exemplo.guia.pergunta", vai_para = "a", uso_unico = true },
  { id = "tchau", texto = "exemplo.guia.tchau", vai_para = "fim" },
]
"""
)


@pytest.fixture
def interacao():
    return Interacao(Cenas.de_toml(CENAS), ROTEIROS, DIALOGOS)


def objeto(partida, id_objeto):
    return next(obj for obj in partida.objetos() if obj.id == id_objeto)


def confirmar_tudo(partida):
    """Confirma as falas até a sequência acabar; devolve as ações vistas."""
    vistas = []
    while partida.diretor.ocupado:
        vistas.append(partida.diretor.acao_atual)
        assert partida.confirmar(), f"esperava uma fala, veio {partida.diretor.acao_atual!r}"
    return vistas


def comecar(interacao):
    """Jogo novo com as boas-vindas já confirmadas."""
    partida = Partida.nova(interacao)
    partida.atualizar(0)
    confirmar_tudo(partida)
    assert partida.atualizar(0)
    return partida


# --- Começo e entrada nas cenas -------------------------------------------------------------


def test_jogo_novo_comeca_na_cena_inicial(interacao):
    partida = Partida.nova(interacao)
    assert partida.estado.cena_atual == "exemplo.sala"
    assert partida.cena.id == "exemplo.sala"


def test_jogo_novo_sem_inicio_e_erro():
    cenas = Cenas.de_toml(CENAS.replace('inicio = "exemplo.sala"', ""))
    sem_inicio = Interacao(cenas, ROTEIROS, DIALOGOS)
    with pytest.raises(ValueError, match="inicio"):
        Partida.nova(sem_inicio)


def test_cena_nova_fica_ocupada_ate_a_entrada_rodar(interacao):
    partida = Partida.nova(interacao)
    assert partida.ocupada
    assert not partida.agir(objeto(partida, "folheto"), Verbo.OLHAR)


def test_entrada_roda_e_o_fim_dela_e_a_hora_do_autosave(interacao):
    partida = Partida.nova(interacao)
    assert not partida.atualizar(0)
    assert partida.diretor.acao_atual == Fala("exemplo.chegada.ola")
    assert partida.estado.tem_flag("exemplo.sala.visitou")
    assert not partida.atualizar(0), "a entrada ainda espera o jogador"
    partida.confirmar()
    assert partida.atualizar(0)
    assert not partida.ocupada
    assert not partida.atualizar(0), "a hora do autosave vem uma vez só"


def test_autosave_grava_a_visita_e_a_entrada_nao_se_repete_ao_continuar(interacao):
    partida = comecar(interacao)
    assert autosalvar(partida.estado, bloqueado=partida.ocupada)

    continuacao = Partida(carregar(), interacao)
    assert continuacao.ocupada
    assert continuacao.atualizar(0), "sem entrada para rodar, a cena fica pronta na hora"
    assert not continuacao.ocupada
    assert not autosalvar(continuacao.estado, bloqueado=continuacao.ocupada), "nada mudou"


def test_autosave_fica_bloqueado_durante_a_entrada(interacao):
    partida = Partida.nova(interacao)
    partida.atualizar(0)
    assert not autosalvar(partida.estado, bloqueado=partida.ocupada)
    assert not existe_save()


def test_save_com_cena_que_nao_existe_e_invalido(interacao):
    estado = EstadoJogo()
    estado.entrar_na_cena("exemplo.sumiu")
    with pytest.raises(SaveInvalido, match="exemplo.sumiu"):
        Partida(estado, interacao)
    with pytest.raises(SaveInvalido):
        Partida(EstadoJogo(), interacao)


# --- Verbos e input bloqueado ---------------------------------------------------------------


def test_verbo_roda_a_resposta_do_objeto(interacao):
    partida = comecar(interacao)
    assert partida.agir(objeto(partida, "folheto"), Verbo.OLHAR)
    assert confirmar_tudo(partida) == [Fala("exemplo.folheto.olhar")]


def test_verbo_sem_resposta_usa_a_recusa(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "folheto"), Verbo.FALAR)
    assert confirmar_tudo(partida) == [Fala("exemplo.recusa.falar")]


def test_input_bloqueado_enquanto_a_sequencia_roda(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "folheto"), Verbo.OLHAR)
    assert partida.ocupada
    assert not partida.agir(objeto(partida, "guia"), Verbo.FALAR)
    assert partida.diretor.acao_atual == Fala("exemplo.folheto.olhar")
    partida.confirmar()
    assert not partida.ocupada
    assert partida.agir(objeto(partida, "guia"), Verbo.FALAR)


def test_item_coletado_some_da_cena(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "folheto"), Verbo.USAR)
    assert not partida.ocupada
    assert partida.estado.tem_item("folheto")
    assert "folheto" not in [obj.id for obj in partida.objetos()]


def test_esperar_segue_com_o_tempo(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "relogio"), Verbo.USAR)
    assert partida.diretor.acao_atual == Esperar(1)
    partida.atualizar(0.6)
    assert partida.diretor.acao_atual == Esperar(1)
    partida.atualizar(0.6)
    assert partida.diretor.acao_atual == Fala("exemplo.relogio.tique")


def test_dialogo_com_escolha_e_opcao_de_uso_unico(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "guia"), Verbo.FALAR)
    partida.confirmar()
    assert partida.diretor.acao_atual == Escolha(("exemplo.guia.pergunta", "exemplo.guia.tchau"))
    partida.escolher(0)
    partida.confirmar()
    assert partida.diretor.acao_atual == Escolha(("exemplo.guia.tchau",))
    partida.escolher(0)
    assert not partida.ocupada


def test_objeto_em_acha_o_objeto_visivel_sob_o_ponto(interacao):
    partida = comecar(interacao)
    assert partida.objeto_em(45, 105).id == "folheto"
    assert partida.objeto_em(0, 0) is None


# --- Troca de cena --------------------------------------------------------------------------


def test_trocar_cena_no_meio_do_roteiro_espera_ele_terminar(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "porta"), Verbo.USAR)
    partida.confirmar()
    # A cena da tela já mudou, mas a entrada do corredor só roda depois da última fala.
    assert partida.cena.id == "exemplo.corredor"
    assert partida.diretor.acao_atual == Fala("x.y")
    assert not partida.atualizar(0)
    assert not partida.estado.tem_flag("exemplo.corredor.visitou")
    partida.confirmar()
    assert partida.ocupada
    assert not partida.atualizar(0)
    assert partida.diretor.acao_atual == Fala("exemplo.corredor.chegada")
    partida.confirmar()
    assert partida.atualizar(0)


def test_voltar_a_uma_cena_visitada_nao_repete_a_entrada(interacao):
    partida = comecar(interacao)
    partida.agir(objeto(partida, "porta"), Verbo.USAR)
    confirmar_tudo(partida)
    partida.atualizar(0)
    confirmar_tudo(partida)
    assert partida.atualizar(0)

    partida.agir(objeto(partida, "volta"), Verbo.USAR)
    assert partida.atualizar(0), "a sala já foi visitada: sem entrada, pronta na hora"
    assert partida.cena.id == "exemplo.sala"
    assert not partida.ocupada


def test_entrada_que_troca_de_cena_prepara_a_seguinte():
    cenas = Cenas.de_toml(
        CENAS.replace(
            'entrada = [{ fala = "exemplo.corredor.chegada" }]',
            'entrada = [{ trocar_cena = "exemplo.sala" }]',
        ).replace('inicio = "exemplo.sala"', 'inicio = "exemplo.corredor"')
    )
    partida = Partida.nova(Interacao(cenas, ROTEIROS, DIALOGOS))
    partida.atualizar(0)
    assert partida.cena.id == "exemplo.sala"
    assert partida.estado.tem_flag("exemplo.corredor.visitou")
    assert partida.diretor.acao_atual == Fala("exemplo.chegada.ola")
    partida.confirmar()
    assert partida.atualizar(0)


# --- Avisos ---------------------------------------------------------------------------------


def test_aviso_aparece_como_fala_e_bloqueia_o_input(interacao):
    partida = comecar(interacao)
    partida.avisar(Fala("exemplo.aviso"))
    assert partida.ocupada
    assert not partida.agir(objeto(partida, "folheto"), Verbo.OLHAR)
    assert confirmar_tudo(partida) == [Fala("exemplo.aviso")]
