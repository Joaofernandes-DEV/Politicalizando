import pytest

from politicalizando.conteudo import carregar_cenas
from politicalizando.dominio.acoes import DarItem, Fala, MarcarFlag
from politicalizando.dominio.cenas import (
    Area,
    CenaInvalida,
    Cenas,
    Resposta,
    Verbo,
    conferir_referencias,
)
from politicalizando.dominio.estado_jogo import EstadoJogo

# Cena de exemplo, neutra e provisória: só existe nos testes.
RECUSAS = """
[recusas]
olhar = ["exemplo.recusa.olhar_1", "exemplo.recusa.olhar_2"]
usar = ["exemplo.recusa.usar_1"]
falar = ["exemplo.recusa.falar_1"]
"""

EXEMPLO = (
    RECUSAS
    + """
[cenas.exemplo.sala]
entrada = { roteiro = "exemplo.chegada" }

[[cenas.exemplo.sala.objetos]]
id = "folheto"
nome = "exemplo.folheto.nome"
area = [40, 100, 16, 12]
olhar = [{ fala = "exemplo.folheto.olhar" }]
usar = [{ dar_item = "folheto" }, { marcar_flag = "exemplo.pegou_folheto" }]
se_nao_item = ["folheto"]

[[cenas.exemplo.sala.objetos]]
id = "guia"
nome = "exemplo.guia.nome"
area = [200, 80, 24, 48]
falar = { dialogo = "exemplo.guia" }
se = ["exemplo.sala.visitou"]

[cenas.exemplo.corredor]
[[cenas.exemplo.corredor.objetos]]
id = "porta"
nome = "exemplo.porta.nome"
area = [0, 0, 320, 180]
usar = { roteiro = "exemplo.sair" }
se_item = ["chave"]
"""
)


def test_carrega_cenas_objetos_e_recusas():
    cenas = Cenas.de_toml(EXEMPLO)
    assert set(cenas) == {"exemplo.sala", "exemplo.corredor"}
    assert cenas.recusas[Verbo.OLHAR] == ("exemplo.recusa.olhar_1", "exemplo.recusa.olhar_2")

    sala = cenas["exemplo.sala"]
    assert sala.entrada == Resposta(roteiro="exemplo.chegada")
    assert sala.flag_visitou == "exemplo.sala.visitou"
    folheto, guia = sala.objetos
    assert (folheto.id, folheto.nome, folheto.area) == (
        "folheto",
        "exemplo.folheto.nome",
        Area(40, 100, 16, 12),
    )
    assert folheto.respostas[Verbo.OLHAR] == Resposta(passos=(Fala("exemplo.folheto.olhar"),))
    assert folheto.respostas[Verbo.USAR].passos == (
        DarItem("folheto"),
        MarcarFlag("exemplo.pegou_folheto"),
    )
    assert Verbo.FALAR not in folheto.respostas
    assert folheto.se_nao_item == {"folheto"}
    assert guia.respostas[Verbo.FALAR] == Resposta(dialogo="exemplo.guia")
    assert guia.se == {"exemplo.sala.visitou"}
    assert cenas["exemplo.corredor"].entrada is None


def test_arquivo_sem_cenas_dispensa_as_recusas():
    cenas = Cenas.de_toml("# só um comentário\n")
    assert len(cenas) == 0
    assert dict(cenas.recusas) == {}


@pytest.mark.parametrize(
    "area",
    [(0, 0, 320, 180), (10, 20, 1, 1), (319, 179, 1, 1)],
)
def test_area_dentro_da_tela_e_aceita(area):
    assert Area(*area).largura == area[2]


@pytest.mark.parametrize(
    "area",
    [
        (0, 0, 0, 10),
        (0, 0, 10, -1),
        (-1, 0, 10, 10),
        (0, -1, 10, 10),
        (311, 0, 10, 10),
        (0, 171, 10, 10),
        (0.5, 0, 10, 10),
        (True, 0, 10, 10),
        ("0", 0, 10, 10),
    ],
    ids=repr,
)
def test_area_invalida_e_recusada(area):
    with pytest.raises(ValueError):
        Area(*area)


def test_area_contem_a_borda_de_cima_e_da_esquerda():
    area = Area(10, 20, 5, 4)
    assert area.contem(10, 20)
    assert area.contem(14.9, 23.9)
    assert not area.contem(15, 20)
    assert not area.contem(10, 24)
    assert not area.contem(9.9, 21)


def _cena(objeto: str = "", extra: str = "", recusas: str = RECUSAS) -> str:
    base = 'id = "a"\nnome = "exemplo.a"\narea = [0, 0, 10, 10]\n'
    return f"{recusas}\n[cenas.sala]\n{extra}\n[[cenas.sala.objetos]]\n{base}{objeto}"


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[cenas", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('mapa = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param("cenas = 1", "deveria ser uma tabela", id="cenas-nao-e-tabela"),
        pytest.param("[cenas]\nsala = 1", "valor solto", id="valor-solto"),
        pytest.param(_cena(recusas=""), "faltam as recusas", id="sem-recusas"),
        pytest.param(
            _cena(recusas=RECUSAS.replace('falar = ["exemplo.recusa.falar_1"]', "")),
            "'falar' precisa",
            id="recusa-faltando",
        ),
        pytest.param(
            _cena(recusas=RECUSAS.replace('["exemplo.recusa.usar_1"]', "[]")),
            "'usar' precisa",
            id="recusa-vazia",
        ),
        pytest.param(
            _cena(recusas=RECUSAS + 'pensar = ["exemplo.x"]'),
            "chaves inesperadas",
            id="recusa-de-verbo-desconhecido",
        ),
        pytest.param(
            _cena(
                recusas=RECUSAS.replace('["exemplo.recusa.usar_1"]', '["exemplo.u", "exemplo.u"]')
            ),
            "repetidos",
            id="recusa-repetida",
        ),
        pytest.param(
            RECUSAS + "[cenas.sala]\nobjetos = []", "pelo menos um objeto", id="sem-objetos"
        ),
        pytest.param(_cena(extra="musica = 1"), "chaves inesperadas", id="chave-extra-na-cena"),
        pytest.param(_cena("pontos = 1"), "chaves inesperadas", id="chave-extra-no-objeto"),
        pytest.param(
            RECUSAS + '[cenas.sala]\nobjetos = [{ id = "a", area = [0, 0, 1, 1] }]',
            "falta a chave 'nome'",
            id="objeto-sem-nome",
        ),
        pytest.param(_cena().replace('id = "a"', 'id = "a.b"'), "id inválido", id="id-com-ponto"),
        pytest.param(_cena().replace('"exemplo.a"', '"Nome"'), "objeto 1", id="nome-invalido"),
        pytest.param(
            _cena().replace("[0, 0, 10, 10]", "[0, 0, 10]"), "x, y, largura", id="area-com-3"
        ),
        pytest.param(
            _cena().replace("[0, 0, 10, 10]", "[315, 0, 10, 10]"), "sai da tela", id="area-fora"
        ),
        pytest.param(_cena("olhar = []"), "lista de passos está vazia", id="passos-vazios"),
        pytest.param(
            _cena('olhar = [{ escolha = ["exemplo.x"] }]'), "olhar, passo 1", id="escolha"
        ),
        pytest.param(_cena('usar = "exemplo.x"'), "use uma lista de passos", id="resposta-texto"),
        pytest.param(
            _cena('usar = { cena = "exemplo.x" }'), "use uma lista de passos", id="resposta-tipo"
        ),
        pytest.param(
            _cena('usar = { roteiro = "a", dialogo = "b" }'),
            "use uma lista de passos",
            id="resposta-dupla",
        ),
        pytest.param(_cena('falar = { dialogo = "Guia" }'), "falar", id="dialogo-id-invalido"),
        pytest.param(_cena('se = "exemplo.f"'), "lista de IDs", id="se-texto"),
        pytest.param(_cena('se_nao_item = ["Folheto"]'), "se_nao_item", id="item-invalido"),
        pytest.param(_cena(extra='entrada = "exemplo.x"'), "entrada", id="entrada-texto"),
        pytest.param(
            _cena() + '\n[[cenas.sala.objetos]]\nid = "a"\nnome = "exemplo.b"\narea = [0, 0, 1, 1]',
            "objetos repetidos",
            id="objeto-repetido",
        ),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(CenaInvalida, match=trecho_da_mensagem):
        Cenas.de_toml(conteudo)


def test_cena_inexistente_levanta_keyerror_com_o_id():
    with pytest.raises(KeyError, match="exemplo.nao_existe"):
        Cenas.de_toml(EXEMPLO)["exemplo.nao_existe"]


def test_conferir_referencias_acusa_roteiro_e_dialogo_inexistentes():
    cenas = Cenas.de_toml(EXEMPLO)
    with pytest.raises(CenaInvalida, match="roteiro 'exemplo.sair'.*diálogo 'exemplo.guia'"):
        conferir_referencias(cenas, {"exemplo.chegada": None}, {})
    conferir_referencias(
        cenas, {"exemplo.chegada": None, "exemplo.sair": None}, {"exemplo.guia": None}
    )


# --- Visibilidade --------------------------------------------------------------------------


def test_objeto_some_depois_de_coletado():
    folheto = Cenas.de_toml(EXEMPLO)["exemplo.sala"].objetos[0]
    estado = EstadoJogo()
    assert folheto.visivel(estado)
    estado.dar_item("folheto")
    assert not folheto.visivel(estado)


def test_objeto_com_se_aparece_so_com_a_flag():
    guia = Cenas.de_toml(EXEMPLO)["exemplo.sala"].objetos[1]
    estado = EstadoJogo()
    assert not guia.visivel(estado)
    estado.marcar_flag("exemplo.sala.visitou")
    assert guia.visivel(estado)


def test_objeto_com_se_item_aparece_so_com_o_item():
    porta = Cenas.de_toml(EXEMPLO)["exemplo.corredor"].objetos[0]
    estado = EstadoJogo()
    assert not porta.visivel(estado)
    estado.dar_item("chave")
    assert porta.visivel(estado)


def test_objeto_com_se_nao_some_com_a_flag():
    cenas = Cenas.de_toml(_cena('se_nao = ["exemplo.fechou"]'))
    objeto = cenas["sala"].objetos[0]
    estado = EstadoJogo()
    assert objeto.visivel(estado)
    estado.marcar_flag("exemplo.fechou")
    assert not objeto.visivel(estado)


# --- Conteúdo ------------------------------------------------------------------------------


def test_dados_usados_pelas_cenas():
    cenas = Cenas.de_toml(EXEMPLO)
    assert cenas.ids_de_texto() == {
        "exemplo.folheto.nome",
        "exemplo.guia.nome",
        "exemplo.porta.nome",
        "exemplo.folheto.olhar",
        "exemplo.recusa.olhar_1",
        "exemplo.recusa.olhar_2",
        "exemplo.recusa.usar_1",
        "exemplo.recusa.falar_1",
    }
    assert cenas.flags_exigidas() == {"exemplo.sala.visitou"}
    assert cenas.flags_marcadas() == {
        "exemplo.sala.visitou",
        "exemplo.corredor.visitou",
        "exemplo.pegou_folheto",
    }
    assert cenas.itens_exigidos() == {"folheto", "chave"}
    assert cenas.itens_dados() == {"folheto"}
    assert cenas.roteiros_usados() == {"exemplo.chegada", "exemplo.sair"}
    assert cenas.dialogos_usados() == {"exemplo.guia"}


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    linhas = (files("politicalizando.conteudo") / "cenas.toml").read_text("utf-8").splitlines()
    inicio = linhas.index("# Exemplo:") + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    cenas = Cenas.de_toml("\n".join(exemplo))
    assert list(cenas) == ["praca"]
    assert [objeto.id for objeto in cenas["praca"].objetos] == ["folheto", "vendedor"]


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_cenas(), Cenas)
