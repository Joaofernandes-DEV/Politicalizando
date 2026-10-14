"""Toda flag e todo item citados numa condição têm origem em algum lugar dos dados.

Pega erros de digitação: uma condição com uma flag que nunca é marcada (ou um item que nunca é
dado) esconderia ou mostraria uma opção ou um objeto para sempre. As condições vêm dos diálogos
(`se`, `se_nao`) e das cenas (`se`, `se_nao`, `se_item`, `se_nao_item`). As origens vêm dos
roteiros, dos diálogos e das cenas (inclusive as `<cena>.visitou`). Quando surgir um roteiro
especial em Python que marque flags ou dê itens, a varredura de código de
`test_textos_usados.py` passa a coletar também `MarcarFlag("...")` e `DarItem("...")`.
"""

from collections.abc import Iterator

from politicalizando.conteudo import carregar_cenas, carregar_dialogos, carregar_roteiros
from politicalizando.dominio.acoes import Acao, DarItem, MarcarFlag
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.roteiro import Roteiros


def _acoes(roteiros: Roteiros, dialogos: Dialogos) -> Iterator[Acao]:
    for sequencia in roteiros.values():
        yield from sequencia.acoes
    for dialogo in dialogos.values():
        for no in dialogo.nos.values():
            yield from no.passos


def flags_sem_origem(roteiros: Roteiros, dialogos: Dialogos, cenas: Cenas) -> list[str]:
    exigidas = dialogos.flags_exigidas() | cenas.flags_exigidas()
    marcadas = {acao.flag for acao in _acoes(roteiros, dialogos) if isinstance(acao, MarcarFlag)}
    marcadas |= dialogos.flags_marcadas() | cenas.flags_marcadas()
    return sorted(exigidas - marcadas)


def itens_sem_origem(roteiros: Roteiros, dialogos: Dialogos, cenas: Cenas) -> list[str]:
    dados = {acao.item for acao in _acoes(roteiros, dialogos) if isinstance(acao, DarItem)}
    return sorted(cenas.itens_exigidos() - dados - cenas.itens_dados())


RECUSAS = '[recusas]\nolhar = ["exemplo.r"]\nusar = ["exemplo.r"]\nfalar = ["exemplo.r"]\n'


def _cena(condicao: str) -> Cenas:
    return Cenas.de_toml(
        RECUSAS + "[cenas.sala]\n"
        f'objetos = [{{ id = "a", nome = "exemplo.a", area = [0, 0, 1, 1], {condicao} }}]'
    )


def test_flag_exigida_marcada_por_um_roteiro_ou_dialogo_passa():
    roteiros = Roteiros.de_toml('exemplo.entrada = [{ marcar_flag = "exemplo.visitou" }]')
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\nopcoes = ['
        '{ id = "x", texto = "exemplo.x", vai_para = "fim", se = ["exemplo.visitou"] },'
        '{ id = "y", texto = "exemplo.y", vai_para = "fim", se_nao = ["exemplo.guia.x"] }]'
    )
    assert flags_sem_origem(roteiros, dialogos, Cenas()) == []


def test_flag_exigida_que_ninguem_marca_e_acusada():
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\nopcoes = ['
        '{ id = "x", texto = "exemplo.x", vai_para = "fim", se = ["exemplo.visituo"] }]'
    )
    assert flags_sem_origem(Roteiros(), dialogos, Cenas()) == ["exemplo.visituo"]


def test_flag_de_visita_da_cena_conta_como_marcada():
    cenas = _cena('se = ["sala.visitou"], se_nao = ["sala.visitu"]')
    assert flags_sem_origem(Roteiros(), Dialogos(), cenas) == ["sala.visitu"]


def test_item_exigido_precisa_ser_dado_em_algum_lugar():
    cenas = _cena('se_item = ["chave"], se_nao_item = ["folheto"]')
    assert itens_sem_origem(Roteiros(), Dialogos(), cenas) == ["chave", "folheto"]

    roteiros = Roteiros.de_toml('exemplo.achar = [{ dar_item = "chave" }]')
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\npassos = [{ dar_item = "folheto" }]'
    )
    assert itens_sem_origem(roteiros, dialogos, cenas) == []


def test_toda_flag_e_todo_item_exigidos_nos_dados_do_jogo_tem_origem():
    dados = (carregar_roteiros(), carregar_dialogos(), carregar_cenas())
    assert flags_sem_origem(*dados) == []
    assert itens_sem_origem(*dados) == []
