import pytest

from politicalizando.dominio.estado_jogo import (
    VERSAO_SAVE,
    EstadoJogo,
    SaveInvalido,
    validar_id,
)


def estado_salvo() -> EstadoJogo:
    """Estado com um pouco de progresso, já marcado como salvo."""
    estado = EstadoJogo()
    estado.entrar_na_cena("praca")
    estado.marcar_flag("praca.visitou")
    estado.marcar_flag("biblioteca.ouviu_bibliotecaria")
    estado.dar_item("panfleto_do_feed")
    estado.dar_item("caderno")
    estado.marcar_salvo()
    return estado


def test_estado_novo_comeca_vazio():
    estado = EstadoJogo()
    assert estado.cena_atual is None
    assert estado.flags == frozenset()
    assert estado.inventario == ()
    assert not estado.alterado


def test_marcar_flag_marca_e_avisa_quando_ja_estava_marcada():
    estado = EstadoJogo()
    assert not estado.tem_flag("praca.visitou")
    assert estado.marcar_flag("praca.visitou")
    assert estado.tem_flag("praca.visitou")
    assert estado.alterado

    estado.marcar_salvo()
    assert not estado.marcar_flag("praca.visitou")
    assert not estado.alterado


def test_inventario_mantem_a_ordem_e_nao_duplica():
    estado = EstadoJogo()
    assert estado.dar_item("panfleto_do_feed")
    assert estado.dar_item("caderno")
    assert not estado.dar_item("panfleto_do_feed")
    assert estado.inventario == ("panfleto_do_feed", "caderno")
    assert estado.tem_item("caderno")


def test_tirar_item():
    estado = estado_salvo()
    assert estado.tirar_item("panfleto_do_feed")
    assert not estado.tem_item("panfleto_do_feed")
    assert estado.inventario == ("caderno",)
    assert estado.alterado


def test_tirar_item_ausente_nao_muda_nada():
    estado = estado_salvo()
    assert not estado.tirar_item("chave")
    assert not estado.alterado


def test_entrar_na_cena_so_altera_se_a_cena_mudar():
    estado = estado_salvo()
    assert not estado.entrar_na_cena("praca")
    assert not estado.alterado

    assert estado.entrar_na_cena("biblioteca")
    assert estado.cena_atual == "biblioteca"
    assert estado.alterado


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "Praca",
        "praca visitou",
        "praça",
        "praca.",
        ".praca",
        "praca..visitou",
        "praca-1",
        3,
        None,
    ],
)
def test_id_invalido_e_recusado(texto):
    with pytest.raises(ValueError):
        validar_id(texto)
    estado = EstadoJogo()
    for operacao in (estado.marcar_flag, estado.dar_item, estado.entrar_na_cena):
        with pytest.raises(ValueError):
            operacao(texto)
    assert not estado.alterado


@pytest.mark.parametrize("texto", ["praca", "biblioteca.ouviu_bibliotecaria", "caso_2.checou"])
def test_id_valido_e_aceito(texto):
    assert validar_id(texto) == texto


def test_flags_e_inventario_nao_vazam_mutacao():
    estado = estado_salvo()
    lista = list(estado.inventario)
    lista.append("intruso")
    assert "intruso" not in estado.inventario
    assert isinstance(estado.flags, frozenset)


def test_para_dict_segue_o_formato_do_save():
    assert estado_salvo().para_dict() == {
        "versao": VERSAO_SAVE,
        "cena_atual": "praca",
        "flags": ["biblioteca.ouviu_bibliotecaria", "praca.visitou"],
        "inventario": ["panfleto_do_feed", "caderno"],
    }


def test_ida_e_volta_preserva_o_estado():
    original = estado_salvo()
    copia = EstadoJogo.de_dict(original.para_dict())
    assert copia.cena_atual == original.cena_atual
    assert copia.flags == original.flags
    assert copia.inventario == original.inventario
    assert not copia.alterado


def test_ida_e_volta_do_estado_novo():
    copia = EstadoJogo.de_dict(EstadoJogo().para_dict())
    assert copia.cena_atual is None
    assert copia.flags == frozenset()
    assert copia.inventario == ()


def _com(**mudancas):
    dados = estado_salvo().para_dict()
    dados.update(mudancas)
    return dados


def _sem(chave):
    dados = estado_salvo().para_dict()
    del dados[chave]
    return dados


@pytest.mark.parametrize(
    "dados",
    [
        pytest.param([], id="nao-e-objeto"),
        pytest.param(_com(versao=VERSAO_SAVE + 1), id="versao-futura"),
        pytest.param(_com(versao="1"), id="versao-texto"),
        pytest.param(_com(versao=True), id="versao-booleana"),
        pytest.param(_sem("flags"), id="chave-faltando"),
        pytest.param(_com(pontos=10), id="chave-extra"),
        pytest.param(_com(cena_atual=7), id="cena-numero"),
        pytest.param(_com(flags="praca.visitou"), id="flags-texto"),
        pytest.param(_com(flags=["Praca"]), id="flag-invalida"),
        pytest.param(_com(inventario=["caderno", "caderno"]), id="item-repetido"),
        pytest.param(_com(inventario=[None]), id="item-nulo"),
    ],
)
def test_de_dict_recusa_dados_malformados(dados):
    with pytest.raises(SaveInvalido):
        EstadoJogo.de_dict(dados)


def test_estado_nao_tem_medidor_de_corrente():
    # E1: o save guarda só flags de evento, itens e a cena; nenhuma pontuação ou alinhamento.
    assert set(EstadoJogo().para_dict()) == {"versao", "cena_atual", "flags", "inventario"}
