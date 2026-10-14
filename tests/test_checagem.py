import pytest

from politicalizando.conteudo import carregar_checagem
from politicalizando.dominio.acoes import Escolha, Fala
from politicalizando.dominio.checagem import (
    ORDEM_DAS_CLASSES,
    SEM_LADO,
    CasoInvalido,
    Casos,
    Classe,
    Tecnica,
    TipoCaso,
)
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.diretor import Diretor
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.fontes import Fonte

# Casos fictícios e neutros: só IDs de exemplo e uma fonte fictícia.
FONTE = 'fontes = [{ autor = "Exemplo, Autor", titulo = "Obra", ano = 2020, editora = "Ed." }]'

FATO = f"""
[casos.exemplo.cartaz]
tipo = "manchete"
conteudo = "exemplo.cartaz.texto"
classe = "fato"
confere = false
explicacao = "exemplo.cartaz.explicacao"
{FONTE}
"""

OPINIAO = """
[casos.exemplo.comentario]
tipo = "fala"
conteudo = "exemplo.comentario.texto"
classe = "opiniao"
explicacao = "exemplo.comentario.explicacao"
"""

MANIPULACAO = """
[casos.exemplo.premio]
tipo = "post"
conteudo = "exemplo.premio.texto"
classe = "manipulacao"
origem = "sem_lado"
tecnica = "golpe"
explicacao = "exemplo.premio.explicacao"
"""

ROTULOS = Escolha(
    ("checagem.classe.fato", "checagem.classe.opiniao", "checagem.classe.manipulacao")
)


def test_carrega_as_tres_classes():
    casos = Casos.de_toml(FATO + OPINIAO + MANIPULACAO)
    assert set(casos) == {"exemplo.cartaz", "exemplo.comentario", "exemplo.premio"}

    fato = casos["exemplo.cartaz"]
    assert (fato.tipo, fato.classe, fato.confere) == (TipoCaso.MANCHETE, Classe.FATO, False)
    assert fato.conteudo == "exemplo.cartaz.texto"
    assert fato.explicacao == "exemplo.cartaz.explicacao"
    assert fato.fontes == (Fonte(autor="Exemplo, Autor", titulo="Obra", ano=2020, editora="Ed."),)
    assert (fato.origem, fato.tecnica) == (None, None)

    opiniao = casos["exemplo.comentario"]
    assert (opiniao.classe, opiniao.confere, opiniao.origem, opiniao.fontes) == (
        Classe.OPINIAO,
        None,
        None,
        (),
    )

    manipulacao = casos["exemplo.premio"]
    assert (manipulacao.classe, manipulacao.origem, manipulacao.tecnica) == (
        Classe.MANIPULACAO,
        SEM_LADO,
        Tecnica.GOLPE,
    )


@pytest.mark.parametrize("origem", [*CORRENTES, SEM_LADO])
def test_manipulacao_aceita_as_4_correntes_e_sem_lado(origem):
    caso = Casos.de_toml(MANIPULACAO.replace('"sem_lado"', f'"{origem}"'))["exemplo.premio"]
    assert caso.origem == origem


def test_as_7_tecnicas_iniciais():
    assert [tecnica.value for tecnica in Tecnica] == [
        "fora_de_contexto",
        "dado_falso",
        "manchete_enganosa",
        "apelo_a_emocao",
        "falsa_autoridade",
        "caca_clique",
        "golpe",
    ]


def test_arquivo_sem_casos_gera_catalogo_vazio():
    assert len(Casos.de_toml("# só um comentário\n")) == 0


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[casos", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('mapa = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param("casos = 1", "deveria ser uma tabela", id="casos-nao-e-tabela"),
        pytest.param("[casos]\nexemplo = 1", "valor solto", id="valor-solto"),
        pytest.param(FATO.replace("confere = false\n", ""), "'confere'", id="fato-sem-confere"),
        pytest.param(FATO.replace("false", '"nao"'), "'confere'", id="fato-confere-texto"),
        pytest.param(FATO.replace(FONTE, ""), "pelo menos uma fonte", id="fato-sem-fonte"),
        pytest.param(
            FATO.replace(FONTE, "fontes = []"), "pelo menos uma fonte", id="fontes-vazias"
        ),
        pytest.param(FATO + 'origem = "socialismo"', "não leva ['origem']", id="fato-com-origem"),
        pytest.param(OPINIAO + "confere = true", "não leva ['confere']", id="opiniao-com-confere"),
        pytest.param(
            OPINIAO + 'origem = "liberalismo"', "não leva ['origem']", id="opiniao-com-origem"
        ),
        pytest.param(
            MANIPULACAO.replace('origem = "sem_lado"\n', ""), "'origem'", id="manip-sem-origem"
        ),
        pytest.param(
            MANIPULACAO.replace('tecnica = "golpe"\n', ""), "'tecnica'", id="manip-sem-tecnica"
        ),
        pytest.param(
            MANIPULACAO.replace('"sem_lado"', '"anarquismo"'),
            "origem desconhecida",
            id="origem-desconhecida",
        ),
        pytest.param(
            MANIPULACAO.replace('"golpe"', '"boato"'), "tecnica: valor desconhecido", id="tecnica"
        ),
        pytest.param(
            MANIPULACAO + "confere = false", "não leva ['confere']", id="manip-com-confere"
        ),
        pytest.param(OPINIAO.replace('"fala"', '"video"'), "tipo: valor desconhecido", id="tipo"),
        pytest.param(OPINIAO.replace('"opiniao"', '"boato"'), "classe: valor", id="classe"),
        pytest.param(
            OPINIAO.replace('conteudo = "exemplo.comentario.texto"\n', ""),
            "falta a chave 'conteudo'",
            id="sem-conteudo",
        ),
        pytest.param(
            OPINIAO.replace('"exemplo.comentario.explicacao"', '"Explicacao"'),
            "explicacao",
            id="explicacao-id-invalido",
        ),
        pytest.param(OPINIAO + "pontos = 1", "chaves inesperadas", id="chave-extra"),
        pytest.param(OPINIAO + 'fontes = "livro"', "'fontes' deveria ser uma lista", id="fontes"),
        pytest.param(
            FATO.replace('editora = "Ed."', 'url = "http://x.org"'), "fonte 1", id="fonte-ruim"
        ),
    ],
)
def test_caso_fora_do_formato_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(CasoInvalido, match=trecho_da_mensagem.replace("[", r"\[")):
        Casos.de_toml(conteudo)


def test_caso_inexistente_levanta_keyerror_com_o_id():
    with pytest.raises(KeyError, match="exemplo.nao_existe"):
        Casos.de_toml(FATO)["exemplo.nao_existe"]


# --- Execução ------------------------------------------------------------------------------


def classificar(conteudo: str, id_caso: str, classe: Classe):
    estado = EstadoJogo()
    diretor = Diretor(estado)
    diretor.iniciar(Casos.de_toml(conteudo)[id_caso].executar(estado))
    vistos = [diretor.acao_atual]
    diretor.confirmar()
    vistos.append(diretor.acao_atual)
    diretor.escolher(ORDEM_DAS_CLASSES.index(classe))
    while diretor.ocupado:
        vistos.append(diretor.acao_atual)
        diretor.confirmar()
    return vistos, estado


def test_classificar_certo_marca_checou_e_acertou():
    vistos, estado = classificar(FATO, "exemplo.cartaz", Classe.FATO)
    assert vistos == [
        Fala("exemplo.cartaz.texto"),
        ROTULOS,
        Fala("checagem.resultado.certo"),
        Fala("exemplo.cartaz.explicacao"),
    ]
    assert estado.flags == {"exemplo.cartaz.checou", "exemplo.cartaz.acertou"}


@pytest.mark.parametrize("classe", [Classe.OPINIAO, Classe.MANIPULACAO])
def test_classificar_errado_marca_so_checou_e_explica(classe):
    # J11: errar nunca pune; a explicação aparece do mesmo jeito.
    vistos, estado = classificar(FATO, "exemplo.cartaz", classe)
    assert vistos[2:] == [Fala("checagem.resultado.errado"), Fala("exemplo.cartaz.explicacao")]
    assert estado.flags == {"exemplo.cartaz.checou"}


def test_opiniao_e_manipulacao_tambem_tem_resposta_certa():
    _, estado = classificar(OPINIAO, "exemplo.comentario", Classe.OPINIAO)
    assert estado.tem_flag("exemplo.comentario.acertou")
    _, estado = classificar(MANIPULACAO, "exemplo.premio", Classe.MANIPULACAO)
    assert estado.tem_flag("exemplo.premio.acertou")


def test_as_opcoes_aparecem_sempre_na_mesma_ordem():
    assert ORDEM_DAS_CLASSES == (Classe.FATO, Classe.OPINIAO, Classe.MANIPULACAO)
    vistos, _ = classificar(MANIPULACAO, "exemplo.premio", Classe.FATO)
    assert vistos[1] == ROTULOS


def test_caso_pode_rodar_de_novo():
    caso = Casos.de_toml(OPINIAO)["exemplo.comentario"]
    estado = EstadoJogo()
    diretor = Diretor(estado)
    for _ in range(2):
        diretor.iniciar(caso.executar(estado))
        diretor.confirmar()
        diretor.escolher(1)
        while diretor.ocupado:
            diretor.confirmar()
    assert estado.flags == {"exemplo.comentario.checou", "exemplo.comentario.acertou"}


# --- Conteúdo ------------------------------------------------------------------------------


def test_textos_e_flags_dos_casos():
    casos = Casos.de_toml(FATO + MANIPULACAO)
    assert casos.ids_de_texto() == {
        "exemplo.cartaz.texto",
        "exemplo.cartaz.explicacao",
        "exemplo.premio.texto",
        "exemplo.premio.explicacao",
    }
    assert casos.flags_marcadas() == {
        "exemplo.cartaz.checou",
        "exemplo.cartaz.acertou",
        "exemplo.premio.checou",
        "exemplo.premio.acertou",
    }


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    linhas = (files("politicalizando.conteudo") / "checagem.toml").read_text("utf-8").splitlines()
    inicio = linhas.index("# Exemplo:") + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    assert list(Casos.de_toml("\n".join(exemplo))) == ["praca.cartaz", "feed.golpe_do_premio"]


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_checagem(), Casos)
