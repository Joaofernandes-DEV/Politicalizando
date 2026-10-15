import pytest

from politicalizando.conteudo import carregar_materia
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.materia import (
    FLAG_PUBLICOU,
    Avaliacao,
    Inclusao,
    MateriaInvalida,
    Nivel,
    PecaInvalida,
    Pecas,
    TipoPeca,
    avaliar,
    pecas_disponiveis,
    publicar,
)

# Peças fictícias e neutras: só IDs de exemplo.
EXEMPLO = """
[pecas.exemplo.fato_a]
tipo = "fato"
texto = "exemplo.fato_a"
fonte_se = ["exemplo.fonte_a"]

[pecas.exemplo.fato_b]
tipo = "fato"
texto = "exemplo.fato_b"

[pecas.exemplo.boato]
tipo = "manipulacao"
texto = "exemplo.boato"

[pecas.exemplo.op_lib]
tipo = "opiniao"
texto = "exemplo.op_lib"
de = "exemplo.pessoa_1"
corrente = "liberalismo"

[pecas.exemplo.op_soc]
tipo = "opiniao"
texto = "exemplo.op_soc"
de = "exemplo.pessoa_2"
corrente = "socialismo"

[pecas.exemplo.op_morador]
tipo = "opiniao"
texto = "exemplo.op_morador"
de = "exemplo.pessoa_3"

[pecas.exemplo.escondida]
tipo = "opiniao"
texto = "exemplo.escondida"
de = "exemplo.pessoa_4"
corrente = "conservadorismo"
se = ["exemplo.ouviu_pessoa_4"]
"""

PECAS = Pecas.de_toml(EXEMPLO)
B, P, M = Nivel.BEM_FEITO, Nivel.EM_PARTE, Nivel.PRECISA_MELHORAR


def estado_com(*flags: str) -> EstadoJogo:
    estado = EstadoJogo()
    for flag in flags:
        estado.marcar_flag(flag)
    return estado


def nota(*inclusoes: Inclusao, estado: EstadoJogo | None = None) -> Avaliacao:
    return avaliar(PECAS, estado or estado_com("exemplo.fonte_a"), inclusoes)


def _i(peca: str, citar: bool = False) -> Inclusao:
    return Inclusao(f"exemplo.{peca}", citar)


# --- Formato -------------------------------------------------------------------------------


def test_carrega_os_tres_tipos_de_peca():
    fato = PECAS["exemplo.fato_a"]
    assert (fato.tipo, fato.texto, fato.fonte_se) == (
        TipoPeca.FATO,
        "exemplo.fato_a",
        {"exemplo.fonte_a"},
    )
    assert PECAS["exemplo.boato"].tipo is TipoPeca.MANIPULACAO
    opiniao = PECAS["exemplo.op_lib"]
    assert (opiniao.de, opiniao.corrente) == ("exemplo.pessoa_1", "liberalismo")
    assert PECAS["exemplo.op_morador"].corrente is None
    assert PECAS["exemplo.escondida"].se == {"exemplo.ouviu_pessoa_4"}


def test_arquivo_sem_pecas_gera_catalogo_vazio():
    assert len(Pecas.de_toml("# só um comentário\n")) == 0


OPINIAO = '[pecas.exemplo.p]\ntipo = "opiniao"\ntexto = "exemplo.t"\nde = "exemplo.d"\n'
FATO = '[pecas.exemplo.p]\ntipo = "fato"\ntexto = "exemplo.t"\n'


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[pecas", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('mapa = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param("pecas = 1", "deveria ser uma tabela", id="pecas-nao-e-tabela"),
        pytest.param("[pecas]\nexemplo = 1", "valor solto", id="valor-solto"),
        pytest.param(FATO.replace('"fato"', '"boato"'), "tipo desconhecido", id="tipo"),
        pytest.param(FATO.replace('texto = "exemplo.t"\n', ""), "'texto'", id="sem-texto"),
        pytest.param(FATO.replace('"exemplo.t"', '"Texto"'), "texto", id="texto-invalido"),
        pytest.param(FATO + "pontos = 1", "chaves inesperadas", id="chave-extra"),
        pytest.param(OPINIAO.replace('de = "exemplo.d"\n', ""), "precisa de 'de'", id="sem-de"),
        pytest.param(OPINIAO + 'fonte_se = ["exemplo.f"]', "só um fato", id="fonte-em-opiniao"),
        pytest.param(FATO + 'de = "exemplo.d"', "só uma opinião leva 'de'", id="de-em-fato"),
        pytest.param(
            FATO + 'corrente = "socialismo"', "só uma opinião leva 'corrente'", id="corrente-fato"
        ),
        pytest.param(
            OPINIAO + 'corrente = "anarquismo"', "corrente desconhecida", id="corrente-invalida"
        ),
        pytest.param(FATO + 'se = "exemplo.f"', "lista de flags", id="se-texto"),
        pytest.param(FATO + 'fonte_se = ["Flag"]', "fonte_se", id="fonte-se-invalida"),
    ],
)
def test_peca_fora_do_formato_e_recusada(conteudo, trecho_da_mensagem):
    with pytest.raises(PecaInvalida, match=trecho_da_mensagem):
        Pecas.de_toml(conteudo)


def test_pecas_disponiveis_dependem_das_flags():
    ids = [peca.id for peca in pecas_disponiveis(PECAS, EstadoJogo())]
    assert "exemplo.escondida" not in ids
    ids = [p.id for p in pecas_disponiveis(PECAS, estado_com("exemplo.ouviu_pessoa_4"))]
    assert "exemplo.escondida" in ids


# --- Critério 1: fatos com fonte ---------------------------------------------------------


@pytest.mark.parametrize(
    ("inclusoes", "nivel"),
    [
        pytest.param([], M, id="nenhum-fato"),
        pytest.param([_i("fato_a", True)], B, id="todos-citados"),
        pytest.param([_i("fato_a", True), _i("fato_b", True)], B, id="dois-citados"),
        pytest.param([_i("fato_a", True), _i("fato_b")], P, id="metade-citada"),
        pytest.param([_i("fato_b")], M, id="nenhum-citado"),
        pytest.param([_i("fato_a", True), _i("boato")], P, id="manipulacao-conta-como-erro"),
        pytest.param([_i("fato_a", True), _i("fato_b"), _i("boato")], M, id="um-terco"),
        pytest.param([_i("boato")], M, id="so-manipulacao"),
    ],
)
def test_fatos_com_fonte(inclusoes, nivel):
    assert nota(*inclusoes).fatos == nivel


# --- Critério 2: opiniões atribuídas ------------------------------------------------------


@pytest.mark.parametrize(
    ("inclusoes", "nivel"),
    [
        pytest.param([], M, id="nenhuma-opiniao"),
        pytest.param([_i("op_lib", True), _i("op_morador", True)], B, id="todas-atribuidas"),
        pytest.param([_i("op_lib", True), _i("op_morador")], P, id="metade-atribuida"),
        pytest.param(
            [_i("op_lib", True), _i("op_soc"), _i("op_morador")], M, id="um-terco-atribuido"
        ),
        pytest.param([_i("op_lib")], M, id="nenhuma-atribuida"),
    ],
)
def test_opinioes_atribuidas(inclusoes, nivel):
    assert nota(*inclusoes).atribuicao == nivel


# --- Critério 3: visões com justiça --------------------------------------------------------


@pytest.mark.parametrize(
    ("inclusoes", "nivel"),
    [
        pytest.param([], M, id="nenhuma-visao"),
        pytest.param([_i("op_lib", True)], M, id="uma-corrente-so"),
        pytest.param(
            [_i("op_lib", True), _i("op_morador", True)], M, id="morador-nao-conta-como-visao"
        ),
        pytest.param([_i("op_lib", True), _i("op_soc", True)], B, id="todas-as-ouvidas"),
    ],
)
def test_visoes_com_justica(inclusoes, nivel):
    assert nota(*inclusoes).justica == nivel


def test_justica_em_parte_quando_falta_uma_corrente_ouvida():
    estado = estado_com("exemplo.fonte_a", "exemplo.ouviu_pessoa_4")
    inclusoes = [_i("op_lib", True), _i("op_soc", True)]
    assert nota(*inclusoes, estado=estado).justica == P
    inclusoes.append(_i("escondida", True))
    assert nota(*inclusoes, estado=estado).justica == B


def test_justica_em_parte_quando_uma_corrente_tem_espaco_demais():
    pecas = Pecas.de_toml(
        "".join(
            f'[pecas.exemplo.{n}]\ntipo = "opiniao"\ntexto = "exemplo.{n}"\n'
            f'de = "exemplo.d"\ncorrente = "{corrente}"\n'
            for n, corrente in [
                ("a1", "liberalismo"),
                ("a2", "liberalismo"),
                ("a3", "liberalismo"),
                ("b1", "socialismo"),
            ]
        )
    )
    estado = EstadoJogo()
    equilibrada = [
        Inclusao("exemplo.a1", True),
        Inclusao("exemplo.a2", True),
        Inclusao("exemplo.b1", True),
    ]
    assert avaliar(pecas, estado, equilibrada).justica == B
    desigual = [*equilibrada, Inclusao("exemplo.a3", True)]
    assert avaliar(pecas, estado, desigual).justica == P


# --- Nota total ----------------------------------------------------------------------------


def test_materia_completa_tira_a_nota_maxima():
    avaliacao = nota(_i("fato_a", True), _i("op_lib", True), _i("op_soc", True))
    assert avaliacao == Avaliacao(fatos=B, atribuicao=B, justica=B)
    assert avaliacao.total == 6


def test_materia_vazia_tira_zero():
    assert nota().total == 0


def test_publicar_avalia_e_marca_a_flag():
    estado = estado_com("exemplo.fonte_a")
    avaliacao = publicar(PECAS, estado, [_i("fato_a", True)])
    assert avaliacao.fatos is B
    assert estado.tem_flag(FLAG_PUBLICOU)
    assert PECAS.flags_marcadas() == {FLAG_PUBLICOU}


def test_avaliar_sem_publicar_nao_marca_nada():
    estado = estado_com("exemplo.fonte_a")
    avaliar(PECAS, estado, [_i("fato_a", True)])
    assert estado.flags == {"exemplo.fonte_a"}


# --- Matéria impossível (defeito da tela) -------------------------------------------------


@pytest.mark.parametrize(
    ("inclusoes", "trecho_da_mensagem"),
    [
        pytest.param([Inclusao("exemplo.nao_existe")], "inexistente", id="peca-inexistente"),
        pytest.param([_i("op_lib"), _i("op_lib", True)], "repetida", id="peca-repetida"),
        pytest.param([_i("escondida")], "indisponível", id="peca-indisponivel"),
        pytest.param([_i("boato", True)], "não pode ser citada", id="citar-manipulacao"),
    ],
)
def test_materia_impossivel_e_erro(inclusoes, trecho_da_mensagem):
    with pytest.raises(MateriaInvalida, match=trecho_da_mensagem):
        nota(*inclusoes)


def test_citar_a_fonte_exige_a_flag_de_fonte():
    with pytest.raises(MateriaInvalida, match="não pode ser citada"):
        nota(_i("fato_a", True), estado=EstadoJogo())
    assert nota(_i("fato_a", True)).fatos == B


# --- Conteúdo ------------------------------------------------------------------------------


def test_textos_e_flags_das_pecas():
    assert "exemplo.op_soc" in PECAS.ids_de_texto()
    assert len(PECAS.ids_de_texto()) == len(PECAS)
    assert PECAS.flags_exigidas() == {"exemplo.fonte_a", "exemplo.ouviu_pessoa_4"}


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    linhas = (files("politicalizando.conteudo") / "materia.toml").read_text("utf-8").splitlines()
    inicio = linhas.index("# Exemplo:") + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    assert list(Pecas.de_toml("\n".join(exemplo))) == [
        "biblioteca.horario",
        "biblioteca.visao_a",
    ]


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_materia(), Pecas)
