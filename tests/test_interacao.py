import pytest

from politicalizando.dominio.acoes import Escolha, Fala
from politicalizando.dominio.cenas import CenaInvalida, Cenas, Verbo
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.diretor import Diretor
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.interacao import Interacao, objeto_em, objetos_visiveis
from politicalizando.dominio.roteiro import Roteiros

# Cenas, roteiros e diálogo de exemplo, neutros e provisórios: só existem nos testes.
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
"""
)

ROTEIROS = Roteiros.de_toml(
    """
[exemplo]
chegada = [{ fala = "exemplo.chegada.ola" }, { marcar_flag = "exemplo.chegou" }]
sair = [{ trocar_cena = "exemplo.sala" }]
"""
)
DIALOGOS = Dialogos.de_toml(
    """
[exemplo.guia]
inicio = "a"
[exemplo.guia.nos.a]
passos = [{ fala = "exemplo.guia.ola" }]
opcoes = [{ id = "tchau", texto = "exemplo.guia.tchau", vai_para = "fim" }]
"""
)


@pytest.fixture
def cenas():
    return Cenas.de_toml(EXEMPLO)


@pytest.fixture
def interacao(cenas):
    return Interacao(cenas, ROTEIROS, DIALOGOS)


def rodar(roteiro, estado):
    """Roda o roteiro no diretor, confirmando falas e escolhendo sempre a 1ª opção."""
    diretor = Diretor(estado)
    diretor.iniciar(roteiro)
    vistos = []
    while diretor.ocupado:
        vistos.append(diretor.acao_atual)
        if isinstance(diretor.acao_atual, Escolha):
            diretor.escolher(0)
        else:
            diretor.confirmar()
    return vistos


# --- Objetos na tela -----------------------------------------------------------------------


def test_objetos_visiveis_na_ordem_do_arquivo(cenas):
    sala = cenas["exemplo.sala"]
    estado = EstadoJogo()
    assert [o.id for o in objetos_visiveis(sala, estado)] == ["folheto"]
    estado.marcar_flag("exemplo.sala.visitou")
    assert [o.id for o in objetos_visiveis(sala, estado)] == ["folheto", "guia"]
    estado.dar_item("folheto")
    assert [o.id for o in objetos_visiveis(sala, estado)] == ["guia"]


def test_objeto_em_acha_o_objeto_sob_o_ponto(cenas):
    sala = cenas["exemplo.sala"]
    estado = EstadoJogo()
    assert objeto_em(sala, estado, 45, 105).id == "folheto"
    assert objeto_em(sala, estado, 5, 5) is None


def test_objeto_em_ignora_objeto_invisivel(cenas):
    sala = cenas["exemplo.sala"]
    estado = EstadoJogo()
    assert objeto_em(sala, estado, 210, 100) is None  # guia ainda escondido
    estado.marcar_flag("exemplo.sala.visitou")
    assert objeto_em(sala, estado, 210, 100).id == "guia"


def test_objeto_em_sobreposicao_o_ultimo_fica_por_cima():
    texto = RECUSAS + (
        "[cenas.sala]\n"
        'objetos = [{ id = "fundo", nome = "exemplo.fundo", area = [0, 0, 320, 180] },'
        ' { id = "quadro", nome = "exemplo.quadro", area = [100, 50, 20, 20] }]'
    )
    sala = Cenas.de_toml(texto)["sala"]
    estado = EstadoJogo()
    assert objeto_em(sala, estado, 110, 60).id == "quadro"
    assert objeto_em(sala, estado, 10, 10).id == "fundo"


# --- Verbos --------------------------------------------------------------------------------


def test_verbo_com_passos_em_linha(interacao, cenas):
    estado = EstadoJogo()
    folheto = cenas["exemplo.sala"].objetos[0]
    assert rodar(interacao.agir(estado, folheto, Verbo.OLHAR), estado) == [
        Fala("exemplo.folheto.olhar")
    ]
    rodar(interacao.agir(estado, folheto, "usar"), estado)
    assert estado.inventario == ("folheto",)
    assert estado.tem_flag("exemplo.pegou_folheto")
    assert not folheto.visivel(estado)


def test_verbo_com_dialogo(interacao, cenas):
    estado = EstadoJogo()
    guia = cenas["exemplo.sala"].objetos[1]
    vistos = rodar(interacao.agir(estado, guia, Verbo.FALAR), estado)
    assert vistos == [Fala("exemplo.guia.ola"), Escolha(("exemplo.guia.tchau",))]
    assert estado.tem_flag("exemplo.guia.tchau")


def test_verbo_com_roteiro(interacao, cenas):
    estado = EstadoJogo()
    porta = cenas["exemplo.corredor"].objetos[0]
    rodar(interacao.agir(estado, porta, Verbo.USAR), estado)
    assert estado.cena_atual == "exemplo.sala"


def test_recusas_alternam_por_verbo(interacao, cenas):
    estado = EstadoJogo()
    guia = cenas["exemplo.sala"].objetos[1]  # só responde a "falar"
    folheto = cenas["exemplo.sala"].objetos[0]  # não responde a "falar"
    olhares = [rodar(interacao.agir(estado, guia, Verbo.OLHAR), estado) for _ in range(3)]
    assert olhares == [
        [Fala("exemplo.recusa.olhar_1")],
        [Fala("exemplo.recusa.olhar_2")],
        [Fala("exemplo.recusa.olhar_1")],
    ]
    # O rodízio de um verbo não mexe no de outro.
    assert rodar(interacao.agir(estado, folheto, Verbo.FALAR), estado) == [
        Fala("exemplo.recusa.falar_1")
    ]


def test_verbo_desconhecido_e_erro(interacao, cenas):
    with pytest.raises(ValueError):
        interacao.agir(EstadoJogo(), cenas["exemplo.sala"].objetos[0], "chutar")


# --- Entrada na cena -----------------------------------------------------------------------


def test_entrada_roda_so_na_primeira_visita(interacao):
    estado = EstadoJogo()
    primeira = rodar(interacao.ao_entrar(estado, "exemplo.sala"), estado)
    assert primeira == [Fala("exemplo.chegada.ola")]
    assert estado.tem_flag("exemplo.sala.visitou")
    assert estado.tem_flag("exemplo.chegou")

    assert rodar(interacao.ao_entrar(estado, "exemplo.sala"), estado) == []


def test_cena_sem_entrada_so_marca_a_visita(interacao):
    estado = EstadoJogo()
    assert rodar(interacao.ao_entrar(estado, "exemplo.corredor"), estado) == []
    assert estado.tem_flag("exemplo.corredor.visitou")


def test_entrada_em_cena_inexistente_e_erro(interacao):
    with pytest.raises(KeyError, match="exemplo.nao_existe"):
        interacao.ao_entrar(EstadoJogo(), "exemplo.nao_existe")


def test_interacao_confere_as_referencias_ao_ser_criada(cenas):
    with pytest.raises(CenaInvalida, match="exemplo.guia"):
        Interacao(cenas, ROTEIROS, Dialogos())
