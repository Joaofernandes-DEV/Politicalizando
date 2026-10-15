"""Toda flag e todo item citados numa condição têm origem em algum lugar dos dados.

Pega erros de digitação: uma condição com uma flag que nunca é marcada (ou um item que nunca é
dado) esconderia ou mostraria uma opção, um objeto ou uma ficha para sempre. As condições vêm
dos diálogos (`se`, `se_nao`), das cenas (`se`, `se_nao`, `se_item`, `se_nao_item`) e do
desbloqueio das fichas (`se`), das peças da matéria (`se`, `fonte_se`) e do mapa (`se` do
mapa e de cada local) das entradas do caderno (`se`) e das propostas (`se`). As origens vêm dos
roteiros, dos diálogos, das cenas (inclusive as `<cena>.visitou`) e dos casos de checagem
(`<caso>.checou` e `<caso>.acertou`). Quando surgir um roteiro
especial em Python que marque flags ou dê itens, a varredura de código de
`test_textos_usados.py` passa a coletar também `MarcarFlag("...")` e `DarItem("...")`.
"""

from collections.abc import Iterator

from politicalizando.conteudo import (
    carregar_caderno,
    carregar_cenas,
    carregar_checagem,
    carregar_dialogos,
    carregar_fichas,
    carregar_mapa,
    carregar_materia,
    carregar_propostas,
    carregar_roteiros,
)
from politicalizando.dominio.acoes import Acao, DarItem, MarcarFlag
from politicalizando.dominio.caderno import Caderno
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.checagem import Casos
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.fichas import Fichas
from politicalizando.dominio.mapa import Mapa
from politicalizando.dominio.materia import Pecas
from politicalizando.dominio.propostas import Propostas
from politicalizando.dominio.roteiro import Roteiros


def _acoes(roteiros: Roteiros, dialogos: Dialogos) -> Iterator[Acao]:
    for sequencia in roteiros.values():
        yield from sequencia.acoes
    for dialogo in dialogos.values():
        for no in dialogo.nos.values():
            yield from no.passos


def flags_sem_origem(
    roteiros: Roteiros,
    dialogos: Dialogos,
    cenas: Cenas,
    fichas: Fichas | None = None,
    casos: Casos | None = None,
    pecas: Pecas | None = None,
    mapa: Mapa | None = None,
    caderno: Caderno | None = None,
    propostas: Propostas | None = None,
) -> list[str]:
    exigidas = dialogos.flags_exigidas() | cenas.flags_exigidas()
    if fichas is not None:
        exigidas |= fichas.flags_exigidas()
    if pecas is not None:
        exigidas |= pecas.flags_exigidas()
    if mapa is not None:
        exigidas |= mapa.flags_exigidas()
    if caderno is not None:
        exigidas |= caderno.flags_exigidas()
    if propostas is not None:
        exigidas |= propostas.flags_exigidas()
    marcadas = {acao.flag for acao in _acoes(roteiros, dialogos) if isinstance(acao, MarcarFlag)}
    marcadas |= dialogos.flags_marcadas() | cenas.flags_marcadas()
    if casos is not None:
        marcadas |= casos.flags_marcadas()
    if propostas is not None:
        marcadas |= propostas.flags_marcadas()
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


def test_flag_de_desbloqueio_da_ficha_precisa_de_origem():
    fichas = Fichas.de_toml(
        """
[fichas.socialismo]
se = ["exemplo.guia.posicao", "exemplo.guia.posicoa"]
ideia_central = "exemplo.ideia"
valores = ["exemplo.valor"]
estado = "exemplo.estado"
mercado = "exemplo.mercado"
sociedade = "exemplo.sociedade"
origem = "exemplo.origem"
pensadores = ["exemplo.pensador"]
proposta = "exemplo.proposta"
confusoes = ["exemplo.confusao"]
diferencas_internas = ["exemplo.vertente_1", "exemplo.vertente_2"]
criticas = [
  { texto = "exemplo.critica_1", de = "liberalismo" },
  { texto = "exemplo.critica_2", de = "outras" },
]
fontes = [{ autor = "Exemplo, Autor", titulo = "Obra", ano = 2000, editora = "Ed." }]
"""
    )
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\n'
        'opcoes = [{ id = "posicao", texto = "exemplo.p", vai_para = "fim" }]'
    )
    assert flags_sem_origem(Roteiros(), dialogos, Cenas(), fichas) == ["exemplo.guia.posicoa"]


def test_flags_dos_casos_de_checagem_contam_como_origem():
    casos = Casos.de_toml(
        """
[casos.exemplo.comentario]
tipo = "fala"
conteudo = "exemplo.t"
classe = "opiniao"
explicacao = "exemplo.e"
"""
    )
    cenas = _cena('se = ["exemplo.comentario.checou", "exemplo.comentario.acertou"]')
    assert flags_sem_origem(Roteiros(), Dialogos(), cenas) == [
        "exemplo.comentario.acertou",
        "exemplo.comentario.checou",
    ]
    assert flags_sem_origem(Roteiros(), Dialogos(), cenas, casos=casos) == []


def test_flags_das_pecas_da_materia_precisam_de_origem():
    pecas = Pecas.de_toml(
        """
[pecas.exemplo.fato]
tipo = "fato"
texto = "exemplo.t"
se = ["exemplo.comentario.checou"]
fonte_se = ["exemplo.comentario.acertuo"]
"""
    )
    casos = Casos.de_toml(
        """
[casos.exemplo.comentario]
tipo = "fala"
conteudo = "exemplo.t"
classe = "opiniao"
explicacao = "exemplo.e"
"""
    )
    sem_origem = flags_sem_origem(Roteiros(), Dialogos(), Cenas(), casos=casos, pecas=pecas)
    assert sem_origem == ["exemplo.comentario.acertuo"]


def test_toda_flag_e_todo_item_exigidos_nos_dados_do_jogo_tem_origem():
    dados = (carregar_roteiros(), carregar_dialogos(), carregar_cenas())
    extras = (
        carregar_fichas(),
        carregar_checagem(),
        carregar_materia(),
        carregar_mapa(),
        carregar_caderno(),
        carregar_propostas(),
    )
    assert flags_sem_origem(*dados, *extras) == []
    assert itens_sem_origem(*dados) == []
