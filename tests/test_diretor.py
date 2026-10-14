import pytest

from politicalizando.dominio.acoes import (
    DarItem,
    Escolha,
    Esperar,
    Fala,
    MarcarFlag,
    Roteiro,
    TrocarCena,
)
from politicalizando.dominio.diretor import Diretor
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.persistencia import autosalvar, existe_save

# Roteiros de exemplo, neutros e provisórios: só existem nos testes.


def roteiro_vazio(estado: EstadoJogo) -> Roteiro:
    return
    yield


def so_instantaneas(estado: EstadoJogo) -> Roteiro:
    yield MarcarFlag("exemplo.visitou")
    yield DarItem("caderno")
    yield TrocarCena("biblioteca")


def com_escolha(estado: EstadoJogo) -> Roteiro:
    yield Fala("exemplo.guia.ola")
    resposta = yield Escolha(("exemplo.guia.sim", "exemplo.guia.nao"))
    if resposta == 0:
        yield MarcarFlag("exemplo.aceitou")
    else:
        yield MarcarFlag("exemplo.recusou")
    yield Fala("exemplo.guia.tchau")


def diretor_com(roteiro) -> tuple[Diretor, EstadoJogo]:
    estado = EstadoJogo()
    diretor = Diretor(estado)
    diretor.iniciar(roteiro(estado))
    return diretor, estado


def test_diretor_novo_esta_parado():
    diretor = Diretor(EstadoJogo())
    assert not diretor.ocupado
    assert diretor.acao_atual is None


def test_roteiro_vazio_termina_na_hora():
    diretor, _ = diretor_com(roteiro_vazio)
    assert not diretor.ocupado
    assert diretor.acao_atual is None


def test_acoes_instantaneas_mudam_o_estado_sem_parar():
    diretor, estado = diretor_com(so_instantaneas)
    assert not diretor.ocupado
    assert estado.tem_flag("exemplo.visitou")
    assert estado.inventario == ("caderno",)
    assert estado.cena_atual == "biblioteca"


def test_roteiro_ve_o_estado_que_acabou_de_mudar():
    def roteiro(estado: EstadoJogo) -> Roteiro:
        yield MarcarFlag("exemplo.visitou")
        if estado.tem_flag("exemplo.visitou"):
            yield Fala("exemplo.de_novo")

    diretor, _ = diretor_com(roteiro)
    assert diretor.acao_atual == Fala("exemplo.de_novo")


def test_fala_espera_o_jogador_confirmar():
    diretor, _ = diretor_com(com_escolha)
    assert diretor.ocupado
    assert diretor.acao_atual == Fala("exemplo.guia.ola")

    diretor.atualizar(60)
    assert diretor.acao_atual == Fala("exemplo.guia.ola")

    assert diretor.confirmar()
    assert diretor.acao_atual == Escolha(("exemplo.guia.sim", "exemplo.guia.nao"))


@pytest.mark.parametrize(
    ("indice", "flag_marcada", "flag_ausente"),
    [(0, "exemplo.aceitou", "exemplo.recusou"), (1, "exemplo.recusou", "exemplo.aceitou")],
)
def test_escolha_volta_ao_roteiro_e_muda_o_caminho(indice, flag_marcada, flag_ausente):
    diretor, estado = diretor_com(com_escolha)
    diretor.confirmar()
    assert diretor.escolher(indice)
    assert estado.tem_flag(flag_marcada)
    assert not estado.tem_flag(flag_ausente)
    assert diretor.acao_atual == Fala("exemplo.guia.tchau")

    assert diretor.confirmar()
    assert not diretor.ocupado


@pytest.mark.parametrize("indice", [-1, 2, True, "0", None], ids=repr)
def test_indice_invalido_e_recusado_e_a_escolha_continua(indice):
    diretor, _ = diretor_com(com_escolha)
    diretor.confirmar()
    escolha = diretor.acao_atual
    with pytest.raises(ValueError):
        diretor.escolher(indice)
    assert diretor.acao_atual == escolha
    assert diretor.ocupado


def test_confirmar_nao_responde_uma_escolha():
    diretor, _ = diretor_com(com_escolha)
    diretor.confirmar()
    escolha = diretor.acao_atual
    assert not diretor.confirmar()
    assert diretor.acao_atual == escolha


def test_escolher_sem_escolha_esperando_nao_faz_nada():
    diretor, _ = diretor_com(com_escolha)
    assert not diretor.escolher(0)
    assert diretor.acao_atual == Fala("exemplo.guia.ola")


def test_confirmar_e_escolher_com_o_diretor_parado():
    diretor = Diretor(EstadoJogo())
    assert not diretor.confirmar()
    assert not diretor.escolher(0)
    diretor.atualizar(1)
    assert not diretor.ocupado


def test_esperar_avanca_quando_o_tempo_acaba():
    def roteiro(estado: EstadoJogo) -> Roteiro:
        yield Esperar(1)
        yield MarcarFlag("exemplo.esperou")

    diretor, estado = diretor_com(roteiro)
    assert diretor.acao_atual == Esperar(1)

    assert not diretor.confirmar()
    diretor.atualizar(0.4)
    diretor.atualizar(0.4)
    assert diretor.acao_atual == Esperar(1)
    assert not estado.tem_flag("exemplo.esperou")

    diretor.atualizar(0.2)
    assert estado.tem_flag("exemplo.esperou")
    assert not diretor.ocupado


def test_ocupado_durante_toda_a_sequencia():
    diretor, _ = diretor_com(com_escolha)
    vistos = []
    while diretor.ocupado:
        vistos.append(diretor.acao_atual)
        if isinstance(diretor.acao_atual, Escolha):
            diretor.escolher(0)
        else:
            diretor.confirmar()
    assert vistos == [
        Fala("exemplo.guia.ola"),
        Escolha(("exemplo.guia.sim", "exemplo.guia.nao")),
        Fala("exemplo.guia.tchau"),
    ]
    assert diretor.acao_atual is None


def test_sequencia_com_as_seis_acoes():
    def roteiro(estado: EstadoJogo) -> Roteiro:
        yield TrocarCena("praca")
        yield Fala("exemplo.guia.ola")
        yield Esperar(0.5)
        resposta = yield Escolha(("exemplo.guia.sim", "exemplo.guia.nao"))
        yield DarItem(f"item_{resposta}")
        yield MarcarFlag("exemplo.terminou")

    diretor, estado = diretor_com(roteiro)
    assert estado.cena_atual == "praca"
    assert diretor.confirmar()
    diretor.atualizar(0.5)
    assert diretor.escolher(1)
    assert not diretor.ocupado
    assert estado.inventario == ("item_1",)
    assert estado.tem_flag("exemplo.terminou")


def test_iniciar_com_outra_sequencia_rodando_e_erro():
    diretor, estado = diretor_com(com_escolha)
    with pytest.raises(RuntimeError):
        diretor.iniciar(so_instantaneas(estado))
    assert diretor.acao_atual == Fala("exemplo.guia.ola")
    assert not estado.tem_flag("exemplo.visitou")


def test_depois_do_fim_da_para_iniciar_outra_sequencia():
    diretor, estado = diretor_com(so_instantaneas)
    diretor.iniciar(com_escolha(estado))
    assert diretor.acao_atual == Fala("exemplo.guia.ola")


def test_iniciar_exige_um_gerador():
    diretor = Diretor(EstadoJogo())
    with pytest.raises(TypeError):
        diretor.iniciar(com_escolha)
    assert not diretor.ocupado


def test_roteiro_que_produz_algo_que_nao_e_acao_e_erro_e_libera_o_diretor():
    def roteiro(estado: EstadoJogo) -> Roteiro:
        yield MarcarFlag("exemplo.antes")
        yield "exemplo.ola"
        yield MarcarFlag("exemplo.depois")

    estado = EstadoJogo()
    diretor = Diretor(estado)
    with pytest.raises(TypeError):
        diretor.iniciar(roteiro(estado))
    assert not diretor.ocupado
    assert diretor.acao_atual is None
    assert estado.tem_flag("exemplo.antes")
    assert not estado.tem_flag("exemplo.depois")


def test_erro_dentro_do_roteiro_sobe_e_libera_o_diretor():
    def roteiro(estado: EstadoJogo) -> Roteiro:
        yield Fala("exemplo.ola")
        raise LookupError("defeito no roteiro")

    diretor, _ = diretor_com(roteiro)
    with pytest.raises(LookupError):
        diretor.confirmar()
    assert not diretor.ocupado


def test_autosave_fica_bloqueado_enquanto_a_sequencia_roda():
    # D10: trocar de cena no meio de uma sequência não grava; depois do fim, grava.
    def roteiro(estado: EstadoJogo) -> Roteiro:
        yield TrocarCena("biblioteca")
        yield Fala("exemplo.guia.ola")

    diretor, estado = diretor_com(roteiro)
    assert estado.cena_atual == "biblioteca"
    assert not autosalvar(estado, bloqueado=diretor.ocupado)
    assert not existe_save()

    diretor.confirmar()
    assert autosalvar(estado, bloqueado=diretor.ocupado)
    assert existe_save()
