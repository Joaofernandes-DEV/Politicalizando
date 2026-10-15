import pytest

from politicalizando.conteudo import carregar_propostas
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.propostas import FLAG_COMPAROU, PropostaInvalida, Propostas


def proposta_toml(corrente: str, extra: str = "", sem: tuple[str, ...] = ()) -> str:
    """Proposta fictícia e completa: só IDs de exemplo, sem conteúdo real."""
    linhas = {
        "se": f'se = ["exemplo.{corrente}.ouviu"]',
        "proposta": f'proposta = "exemplo.{corrente}.proposta"',
        "pros": f'pros = ["exemplo.{corrente}.pro"]',
        "contras": f'contras = ["exemplo.{corrente}.contra_1", "exemplo.{corrente}.contra_2"]',
        "valores": f'valores = ["exemplo.{corrente}.valor"]',
    }
    corpo = "\n".join(linha for nome, linha in linhas.items() if nome not in sem)
    return f"[propostas.{corrente}]\n{corpo}\n{extra}\n"


def todas() -> Propostas:
    return Propostas.de_toml("".join(proposta_toml(c) for c in reversed(CORRENTES)))


def test_proposta_completa_carrega():
    proposta = Propostas.de_toml(proposta_toml("socialismo"))["socialismo"]
    assert proposta.proposta == "exemplo.socialismo.proposta"
    assert proposta.pros == ("exemplo.socialismo.pro",)
    assert proposta.contras == ("exemplo.socialismo.contra_1", "exemplo.socialismo.contra_2")
    assert proposta.valores == ("exemplo.socialismo.valor",)
    assert proposta.se == {"exemplo.socialismo.ouviu"}


def test_propostas_ficam_na_ordem_fixa_das_correntes():
    assert list(todas()) == list(CORRENTES)


def test_liberadas_saem_na_ordem_fixa_mesmo_ouvindo_em_outra_ordem():
    propostas = todas()
    estado = EstadoJogo()
    estado.marcar_flag("exemplo.social_democracia.ouviu")
    estado.marcar_flag("exemplo.liberalismo.ouviu")
    assert [p.corrente for p in propostas.liberadas(estado)] == [
        "liberalismo",
        "social_democracia",
    ]


def test_comparar_so_marca_a_flag_com_duas_propostas():
    propostas = todas()
    estado = EstadoJogo()
    estado.marcar_flag("exemplo.socialismo.ouviu")
    assert not propostas.registrar_comparacao(estado)
    assert not estado.tem_flag(FLAG_COMPAROU)
    estado.marcar_flag("exemplo.conservadorismo.ouviu")
    assert propostas.registrar_comparacao(estado)
    assert estado.tem_flag(FLAG_COMPAROU)
    assert not propostas.registrar_comparacao(estado), "a flag já estava marcada"


def test_dados_usados_pelas_propostas():
    propostas = Propostas.de_toml(proposta_toml("liberalismo"))
    assert propostas["liberalismo"].ids_de_texto() == (
        "exemplo.liberalismo.proposta",
        "exemplo.liberalismo.pro",
        "exemplo.liberalismo.contra_1",
        "exemplo.liberalismo.contra_2",
        "exemplo.liberalismo.valor",
    )
    assert propostas.flags_exigidas() == {"exemplo.liberalismo.ouviu"}
    assert propostas.flags_marcadas() == {FLAG_COMPAROU}


def test_arquivo_sem_propostas_gera_catalogo_vazio():
    assert len(Propostas.de_toml("# só um comentário\n")) == 0


@pytest.mark.parametrize("item", ["proposta", "pros", "contras", "valores"])
def test_proposta_sem_um_item_do_modelo_e_recusada(item):
    with pytest.raises(PropostaInvalida, match=f"faltam itens do modelo \\['{item}'\\]"):
        Propostas.de_toml(proposta_toml("conservadorismo", sem=(item,)))


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[propostas", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('mapa = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param("propostas = 1", "deveria ser uma tabela", id="propostas-nao-e-tabela"),
        pytest.param(
            proposta_toml("liberalismo").replace("propostas.liberalismo", "propostas.anarquismo"),
            "corrente desconhecida",
            id="corrente-desconhecida",
        ),
        pytest.param("[propostas]\nliberalismo = 1", "é uma tabela", id="proposta-valor"),
        pytest.param(proposta_toml("liberalismo", "pontos = 1"), "chaves inesperadas", id="extra"),
        pytest.param(
            proposta_toml("liberalismo", "pros = []", sem=("pros",)),
            "pelo menos um item",
            id="lista-vazia",
        ),
        pytest.param(
            proposta_toml("liberalismo", 'proposta = "Proposta"', sem=("proposta",)),
            "proposta 'liberalismo', proposta",
            id="id-invalido",
        ),
        pytest.param(
            proposta_toml("liberalismo", 'se = "exemplo.x"', sem=("se",)),
            "lista de flags",
            id="se-texto",
        ),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(PropostaInvalida, match=trecho_da_mensagem):
        Propostas.de_toml(conteudo)


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    arquivo = files("politicalizando.conteudo") / "propostas.toml"
    linhas = arquivo.read_text("utf-8").splitlines()
    inicio = next(i for i, linha in enumerate(linhas) if linha.startswith("# Exemplo")) + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha.startswith("#   "):
            exemplo.append(linha[4:])
        elif exemplo and linha != "#":
            break
    assert list(Propostas.de_toml("\n".join(exemplo))) == ["liberalismo"]


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_propostas(), Propostas)
