import dataclasses

import pytest

from politicalizando.dominio.acoes import (
    AbrirTela,
    DarItem,
    Escolha,
    Esperar,
    Fala,
    MarcarFlag,
    TrocarCena,
)

IDS_INVALIDOS = ["", "Praca", "praça", "praca-1", "praca..visitou", 3, None]


@pytest.mark.parametrize("tipo", [Fala, MarcarFlag, DarItem, TrocarCena])
@pytest.mark.parametrize("texto", IDS_INVALIDOS)
def test_acao_com_id_invalido_e_recusada(tipo, texto):
    with pytest.raises(ValueError):
        tipo(texto)


@pytest.mark.parametrize("tipo", [Fala, MarcarFlag, DarItem, TrocarCena])
def test_acao_com_id_valido_guarda_o_id(tipo):
    assert dataclasses.astuple(tipo("exemplo.ola")) == ("exemplo.ola",)


def test_escolha_guarda_as_opcoes_como_tupla():
    assert Escolha(["exemplo.sim", "exemplo.nao"]).opcoes == ("exemplo.sim", "exemplo.nao")
    assert Escolha(("exemplo.ok",)).opcoes == ("exemplo.ok",)


@pytest.mark.parametrize(
    "opcoes",
    [
        pytest.param((), id="vazia"),
        pytest.param(("exemplo.sim", "exemplo.sim"), id="repetida"),
        pytest.param(("exemplo.sim", "Nao"), id="id-invalido"),
        pytest.param("exemplo.sim", id="texto-solto"),
        pytest.param(None, id="nula"),
    ],
)
def test_escolha_invalida_e_recusada(opcoes):
    with pytest.raises(ValueError):
        Escolha(opcoes)


@pytest.mark.parametrize("segundos", [0.5, 2])
def test_esperar_aceita_tempo_positivo(segundos):
    espera = Esperar(segundos)
    assert espera.segundos == segundos
    assert isinstance(espera.segundos, float)


@pytest.mark.parametrize("segundos", [0, -1, float("nan"), float("inf"), True, "2", None], ids=repr)
def test_esperar_recusa_tempo_invalido(segundos):
    with pytest.raises(ValueError):
        Esperar(segundos)


@pytest.mark.parametrize(
    "acao",
    [
        Fala("exemplo.ola"),
        Escolha(("exemplo.sim",)),
        Esperar(1),
        MarcarFlag("exemplo.viu"),
        DarItem("caderno"),
        TrocarCena("praca"),
    ],
    ids=lambda acao: type(acao).__name__,
)
def test_acoes_sao_imutaveis_e_comparaveis(acao):
    campo = dataclasses.fields(acao)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(acao, campo, "outro")
    assert acao == dataclasses.replace(acao)
    assert hash(acao) == hash(dataclasses.replace(acao))


def test_abrir_tela_aceita_so_telas_conhecidas():
    assert AbrirTela("comparacao").tela == "comparacao"
    with pytest.raises(ValueError, match="tela desconhecida"):
        AbrirTela("loja")
