from collections.abc import Iterator

import pytest

from politicalizando.conteudo import (
    carregar_caderno,
    carregar_cenas,
    carregar_dialogos,
    carregar_roteiros,
)
from politicalizando.dominio.acoes import DarItem
from politicalizando.dominio.caderno import Caderno, CadernoInvalido, Origem
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.fontes import Fonte

# Caderno de exemplo, neutro e provisório: só existe nos testes.
EXEMPLO = """
[itens]
folheto = "exemplo.item.folheto"
chave = "exemplo.item.chave"

[[entradas]]
id = "guia"
texto = "exemplo.guia.disse"
origem = "opiniao"
de = "exemplo.guia.nome"
se = ["exemplo.guia.posicao"]

[[entradas]]
id = "horario"
texto = "exemplo.horario"
origem = "fato"
fontes = [{ autor = "Prefeitura", titulo = "Horários", ano = 2026, do_jogo = true }]

[[entradas]]
id = "leitura"
texto = "exemplo.leitura"
origem = "interpretacao"
fontes = [{ autor = "Exemplo, Autor", titulo = "Obra", ano = 2000, editora = "Ed." }]
se = ["exemplo.arquivo.leu"]
"""


@pytest.fixture
def caderno():
    return Caderno.de_toml(EXEMPLO)


def test_carrega_entradas_com_a_origem_marcada(caderno):
    guia, horario, leitura = caderno.entradas
    assert (guia.origem, guia.de, guia.fontes) == (Origem.OPINIAO, "exemplo.guia.nome", ())
    assert horario.origem is Origem.FATO
    assert horario.fontes == (Fonte(autor="Prefeitura", titulo="Horários", ano=2026, do_jogo=True),)
    assert leitura.origem is Origem.INTERPRETACAO
    assert leitura.se == {"exemplo.arquivo.leu"}


def test_conversas_e_fontes_aparecem_com_as_flags(caderno):
    estado = EstadoJogo()
    assert caderno.conversas(estado) == ()
    assert [entrada.id for entrada in caderno.fontes(estado)] == ["horario"]
    estado.marcar_flag("exemplo.guia.posicao")
    estado.marcar_flag("exemplo.arquivo.leu")
    assert [entrada.id for entrada in caderno.conversas(estado)] == ["guia"]
    assert [entrada.id for entrada in caderno.fontes(estado)] == ["horario", "leitura"]


def test_itens_saem_na_ordem_de_coleta_e_item_sem_nome_fica_de_fora(caderno):
    estado = EstadoJogo()
    estado.dar_item("chave")
    estado.dar_item("item_de_save_antigo")
    estado.dar_item("folheto")
    assert caderno.itens_do_inventario(estado) == ("exemplo.item.chave", "exemplo.item.folheto")


def test_caderno_nunca_marca_flags(caderno):
    estado = EstadoJogo()
    caderno.conversas(estado)
    caderno.fontes(estado)
    caderno.itens_do_inventario(estado)
    assert estado.flags == frozenset()
    assert not estado.alterado


def test_dados_usados_pelo_caderno(caderno):
    assert caderno.ids_de_texto() == {
        "exemplo.item.folheto",
        "exemplo.item.chave",
        "exemplo.guia.disse",
        "exemplo.guia.nome",
        "exemplo.horario",
        "exemplo.leitura",
    }
    assert caderno.flags_exigidas() == {"exemplo.guia.posicao", "exemplo.arquivo.leu"}


def test_arquivo_sem_nada_gera_caderno_vazio():
    caderno = Caderno.de_toml("# só um comentário\n")
    assert caderno.entradas == ()
    assert dict(caderno.itens) == {}


def _entrada(origem: str, extra: str = "") -> str:
    return f'[[entradas]]\nid = "a"\ntexto = "exemplo.a"\norigem = "{origem}"\n{extra}\n'


FONTE = 'fontes = [{ autor = "A", titulo = "T", ano = 2000, editora = "E" }]'


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[[entradas]", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('mapa = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param('itens = "x"', "'itens' deveria ser uma tabela", id="itens-texto"),
        pytest.param('[itens]\nfolheto = "Folheto"', "itens, folheto", id="nome-de-item-invalido"),
        pytest.param('entradas = "x"', "lista de tabelas", id="entradas-texto"),
        pytest.param("entradas = [1]", "uma entrada é uma tabela", id="entrada-valor"),
        pytest.param(_entrada("fato", f"{FONTE}\npontos = 1"), "chaves inesperadas", id="extra"),
        pytest.param(
            '[[entradas]]\nid = "a"\norigem = "fato"', "falta a chave 'texto'", id="sem-texto"
        ),
        pytest.param(_entrada("boato"), "origem desconhecida", id="origem-desconhecida"),
        pytest.param(_entrada("opiniao"), "precisa de 'de'", id="opiniao-sem-de"),
        pytest.param(
            _entrada("opiniao", f'de = "exemplo.b"\n{FONTE}'),
            "não leva 'fontes'",
            id="opiniao-fonte",
        ),
        pytest.param(_entrada("fato"), "pelo menos uma fonte", id="fato-sem-fonte"),
        pytest.param(
            _entrada("fato", "fontes = []"), "pelo menos uma fonte", id="fato-fontes-vazias"
        ),
        pytest.param(
            _entrada("interpretacao"), "pelo menos uma fonte", id="interpretacao-sem-fonte"
        ),
        pytest.param(_entrada("fato", f'{FONTE}\nde = "exemplo.b"'), "não leva 'de'", id="fato-de"),
        pytest.param(
            _entrada("fato", 'fontes = [{ autor = "A", titulo = "T", ano = 2000 }]'),
            "'editora' ou 'url'",
            id="fonte-real-incompleta",
        ),
        pytest.param(_entrada("opiniao", 'de = "Nome"'), "de: ID inválido", id="de-invalido"),
        pytest.param(_entrada("fato", f'{FONTE}\nse = "x"'), "lista de flags", id="se-texto"),
        pytest.param(
            _entrada("fato", FONTE).replace('"a"', '"a.b"', 1), "id inválido", id="id-com-ponto"
        ),
        pytest.param(
            _entrada("fato", FONTE) + _entrada("fato", FONTE), "repetidas", id="id-repetido"
        ),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(CadernoInvalido, match=trecho_da_mensagem):
        Caderno.de_toml(conteudo)


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    linhas = (files("politicalizando.conteudo") / "caderno.toml").read_text("utf-8").splitlines()
    inicio = linhas.index("# Exemplo:") + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    caderno = Caderno.de_toml("\n".join(exemplo))
    assert [entrada.id for entrada in caderno.entradas] == ["guia_posicao", "orcamento"]


def _itens_dados() -> Iterator[str]:
    yield from carregar_cenas().itens_dados()
    for sequencia in carregar_roteiros().values():
        yield from (acao.item for acao in sequencia.acoes if isinstance(acao, DarItem))
    for dialogo in carregar_dialogos().values():
        for no in dialogo.nos.values():
            yield from (acao.item for acao in no.passos if isinstance(acao, DarItem))


def test_todo_item_que_o_jogo_da_tem_nome_no_caderno():
    sem_nome = sorted(set(_itens_dados()) - set(carregar_caderno().itens))
    assert sem_nome == []
