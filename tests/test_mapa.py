import pytest

from politicalizando.conteudo import carregar_cenas, carregar_mapa
from politicalizando.dominio.cenas import Area
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.mapa import Local, Mapa, MapaInvalido, conferir_cenas

# Mapa de exemplo, neutro e provisório: só existe nos testes.
EXEMPLO = """
se = ["exemplo.tutorial"]

[[locais]]
id = "sala"
nome = "exemplo.mapa.sala"
cena = "exemplo.sala"
area = [10, 20, 60, 30]

[[locais]]
id = "patio"
nome = "exemplo.mapa.patio"
cena = "exemplo.patio"
area = [100, 20, 60, 30]
se = ["exemplo.sala.visitou"]
"""


@pytest.fixture
def mapa():
    return Mapa.de_toml(EXEMPLO)


def test_carrega_os_locais_na_ordem_do_arquivo(mapa):
    sala, patio = mapa.locais
    assert sala == Local("sala", "exemplo.mapa.sala", "exemplo.sala", Area(10, 20, 60, 30))
    assert patio.se == {"exemplo.sala.visitou"}
    assert mapa.se == {"exemplo.tutorial"}


def test_mapa_so_abre_com_as_flags_dele(mapa):
    estado = EstadoJogo()
    assert not mapa.liberado(estado)
    estado.marcar_flag("exemplo.tutorial")
    assert mapa.liberado(estado)


def test_local_bloqueado_fica_escondido(mapa):
    estado = EstadoJogo()
    assert [local.id for local in mapa.locais_liberados(estado)] == ["sala"]
    assert mapa.local_em(estado, 110, 30) is None, "escondido também não recebe clique"
    estado.marcar_flag("exemplo.sala.visitou")
    assert [local.id for local in mapa.locais_liberados(estado)] == ["sala", "patio"]
    assert mapa.local_em(estado, 110, 30).id == "patio"


def test_mapa_sem_locais_liberados_nao_abre():
    mapa = Mapa.de_toml(
        EXEMPLO.replace("area = [10, 20, 60, 30]", 'area = [10, 20, 60, 30]\nse = ["exemplo.x"]')
    )
    estado = EstadoJogo()
    estado.marcar_flag("exemplo.tutorial")
    assert not mapa.liberado(estado)


def test_arquivo_sem_locais_gera_mapa_vazio_que_nunca_abre():
    mapa = Mapa.de_toml("# só um comentário\n")
    assert mapa.locais == ()
    assert not mapa.liberado(EstadoJogo())


def test_dados_usados_pelo_mapa(mapa):
    assert mapa.ids_de_texto() == {"exemplo.mapa.sala", "exemplo.mapa.patio"}
    assert mapa.flags_exigidas() == {"exemplo.tutorial", "exemplo.sala.visitou"}
    assert mapa.cenas_usadas() == {"exemplo.sala", "exemplo.patio"}


def test_conferir_cenas_acusa_destino_inexistente(mapa):
    with pytest.raises(MapaInvalido, match="exemplo.patio"):
        conferir_cenas(mapa, {"exemplo.sala"})
    conferir_cenas(mapa, {"exemplo.sala", "exemplo.patio"})


def _local(extra: str = "", sem: str = "") -> str:
    campos = {
        "id": 'id = "a"',
        "nome": 'nome = "exemplo.a"',
        "cena": 'cena = "exemplo.sala"',
        "area": "area = [0, 0, 10, 10]",
    }
    corpo = "\n".join(linha for nome, linha in campos.items() if nome != sem)
    return f"[[locais]]\n{corpo}\n{extra}\n"


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[[locais]", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('cenas = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param('locais = "x"', "lista de tabelas", id="locais-texto"),
        pytest.param('se = "exemplo.x"', "lista de flags", id="se-texto"),
        pytest.param("locais = [1]", "um local é uma tabela", id="local-valor"),
        pytest.param(_local("pontos = 1"), "chaves inesperadas", id="chave-extra-no-local"),
        pytest.param(_local(sem="cena"), "faltam as chaves \\['cena'\\]", id="sem-cena"),
        pytest.param(_local().replace('"a"', '"a.b"', 1), "id inválido", id="id-com-ponto"),
        pytest.param(_local().replace('"exemplo.a"', '"Nome"'), "local 'a'", id="nome-invalido"),
        pytest.param(_local().replace("[0, 0, 10, 10]", "[0, 0, 10]"), "x, y", id="area-com-3"),
        pytest.param(
            _local().replace("[0, 0, 10, 10]", "[315, 0, 10, 10]"), "sai da tela", id="area-fora"
        ),
        pytest.param(_local('se = ["Flag"]'), "local 'a', se", id="se-invalido"),
        pytest.param(
            _local()
            + _local()
            .replace("[0, 0, 10, 10]", "[20, 0, 10, 10]")
            .replace("exemplo.sala", "exemplo.outra"),
            "mesmo 'id'",
            id="id-repetido",
        ),
        pytest.param(
            _local()
            + _local().replace('"a"', '"b"', 1).replace("[0, 0, 10, 10]", "[20, 0, 10, 10]"),
            "mesmo 'cena'",
            id="cena-repetida",
        ),
        pytest.param(
            _local() + _local().replace('"a"', '"b"', 1).replace("exemplo.sala", "exemplo.outra"),
            "mesmo 'area'",
            id="area-repetida",
        ),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(MapaInvalido, match=trecho_da_mensagem):
        Mapa.de_toml(conteudo)


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    linhas = (files("politicalizando.conteudo") / "mapa.toml").read_text("utf-8").splitlines()
    inicio = linhas.index("# Exemplo:") + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    mapa = Mapa.de_toml("\n".join(exemplo))
    assert [local.id for local in mapa.locais] == ["biblioteca", "praca"]


def test_mapa_do_jogo_carrega_e_leva_a_cenas_que_existem():
    mapa = carregar_mapa()
    assert mapa.cenas_usadas() <= set(carregar_cenas())
