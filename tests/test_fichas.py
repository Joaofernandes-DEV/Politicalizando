import pytest

from politicalizando.conteudo import carregar_fichas
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.fichas import Critica, FichaInvalida, Fichas
from politicalizando.dominio.fontes import Fonte


def ficha_toml(corrente: str, extra: str = "", sem: tuple[str, ...] = ()) -> str:
    """Ficha fictícia e completa: só IDs de exemplo e uma fonte fictícia, sem conteúdo real."""
    outras = [outra for outra in CORRENTES if outra != corrente]
    linhas = {
        "se": f'se = ["exemplo.{corrente}.desbloqueio"]',
        "ideia_central": f'ideia_central = "exemplo.{corrente}.ideia"',
        "valores": f'valores = ["exemplo.{corrente}.valor_1", "exemplo.{corrente}.valor_2"]',
        "estado": f'estado = "exemplo.{corrente}.estado"',
        "mercado": f'mercado = "exemplo.{corrente}.mercado"',
        "sociedade": f'sociedade = "exemplo.{corrente}.sociedade"',
        "origem": f'origem = "exemplo.{corrente}.origem"',
        "pensadores": f'pensadores = ["exemplo.{corrente}.pensador"]',
        "proposta": f'proposta = "exemplo.{corrente}.proposta"',
        "confusoes": f'confusoes = ["exemplo.{corrente}.confusao"]',
        "diferencas_internas": (
            f'diferencas_internas = ["exemplo.{corrente}.vertente_1",'
            f' "exemplo.{corrente}.vertente_2"]'
        ),
        "criticas": (
            f'criticas = [{{ texto = "exemplo.{corrente}.critica_1", de = "{outras[0]}" }},'
            f' {{ texto = "exemplo.{corrente}.critica_2", de = "outras" }}]'
        ),
        "fontes": (
            'fontes = [{ autor = "Exemplo, Autor", titulo = "Obra de exemplo", ano = 2000,'
            ' editora = "Ed." }]'
        ),
    }
    corpo = "\n".join(linha for nome, linha in linhas.items() if nome not in sem)
    return f"[fichas.{corrente}]\n{corpo}\n{extra}\n"


def test_ficha_completa_carrega_com_os_9_itens():
    ficha = Fichas.de_toml(ficha_toml("socialismo"))["socialismo"]
    assert ficha.corrente == "socialismo"
    assert ficha.ideia_central == "exemplo.socialismo.ideia"
    assert ficha.valores == ("exemplo.socialismo.valor_1", "exemplo.socialismo.valor_2")
    assert (ficha.estado, ficha.mercado, ficha.sociedade) == (
        "exemplo.socialismo.estado",
        "exemplo.socialismo.mercado",
        "exemplo.socialismo.sociedade",
    )
    assert ficha.origem == "exemplo.socialismo.origem"
    assert ficha.pensadores == ("exemplo.socialismo.pensador",)
    assert ficha.proposta == "exemplo.socialismo.proposta"
    assert ficha.criticas == (
        Critica("exemplo.socialismo.critica_1", "liberalismo"),
        Critica("exemplo.socialismo.critica_2", "outras"),
    )
    assert ficha.confusoes == ("exemplo.socialismo.confusao",)
    assert ficha.diferencas_internas == (
        "exemplo.socialismo.vertente_1",
        "exemplo.socialismo.vertente_2",
    )
    assert ficha.fontes == (
        Fonte(autor="Exemplo, Autor", titulo="Obra de exemplo", ano=2000, editora="Ed."),
    )
    assert ficha.se == {"exemplo.socialismo.desbloqueio"}


def test_ficha_recusa_fonte_do_jogo():
    fonte = '[{ autor = "Prefeitura", titulo = "Relatório", ano = 2026, do_jogo = true }]'
    with pytest.raises(FichaInvalida, match="não usam fontes do jogo"):
        Fichas.de_toml(_trocar("fontes", f"fontes = {fonte}"))


def test_ficha_sem_se_ja_comeca_desbloqueada():
    ficha = Fichas.de_toml(ficha_toml("liberalismo", sem=("se",)))["liberalismo"]
    assert ficha.se == frozenset()
    assert ficha.desbloqueada(EstadoJogo())


def test_arquivo_sem_fichas_gera_catalogo_vazio():
    assert len(Fichas.de_toml("# só um comentário\n")) == 0


ITENS_OBRIGATORIOS = [
    "ideia_central",
    "valores",
    "estado",
    "mercado",
    "sociedade",
    "origem",
    "pensadores",
    "proposta",
    "criticas",
    "confusoes",
    "diferencas_internas",
    "fontes",
]


@pytest.mark.parametrize("item", ITENS_OBRIGATORIOS)
def test_ficha_sem_um_item_do_modelo_e_recusada(item):
    with pytest.raises(FichaInvalida, match=f"faltam itens do modelo \\['{item}'\\]"):
        Fichas.de_toml(ficha_toml("conservadorismo", sem=(item,)))


def _trocar(item: str, linha: str, corrente: str = "conservadorismo") -> str:
    return ficha_toml(corrente, extra=linha, sem=(item,))


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[fichas", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('mapa = "x"', "chaves inesperadas", id="chave-extra-na-raiz"),
        pytest.param("fichas = 1", "deveria ser uma tabela", id="fichas-nao-e-tabela"),
        pytest.param(
            ficha_toml("liberalismo").replace("fichas.liberalismo", "fichas.anarquismo"),
            "corrente desconhecida",
            id="corrente-desconhecida",
        ),
        pytest.param("[fichas]\nliberalismo = 1", "uma ficha é uma tabela", id="ficha-valor"),
        pytest.param(
            ficha_toml("liberalismo", extra="pontos = 1"), "chaves inesperadas", id="chave-extra"
        ),
        pytest.param(_trocar("valores", "valores = []"), "pelo menos um item", id="lista-vazia"),
        pytest.param(_trocar("fontes", "fontes = []"), "pelo menos um item", id="sem-fonte"),
        pytest.param(
            _trocar("diferencas_internas", "diferencas_internas = []"),
            "pelo menos um item",
            id="sem-vertentes",
        ),
        pytest.param(
            _trocar("diferencas_internas", 'diferencas_internas = ["exemplo.v"]'),
            "pelo menos 2 vertentes",
            id="uma-vertente-so",
        ),
        pytest.param(
            _trocar("diferencas_internas", 'diferencas_internas = ["exemplo.v", "exemplo.v"]'),
            "pelo menos 2 vertentes",
            id="vertente-repetida",
        ),
        pytest.param(
            _trocar("ideia_central", 'ideia_central = "Ideia"'), "ideia_central", id="id-invalido"
        ),
        pytest.param(
            _trocar("pensadores", 'pensadores = ["exemplo.a", 3]'), "pensadores", id="item-numero"
        ),
        pytest.param(
            _trocar("criticas", 'criticas = [{ texto = "exemplo.c", de = "socialismo" }]'),
            "pelo menos 2 origens",
            id="uma-critica-so",
        ),
        pytest.param(
            _trocar(
                "criticas",
                'criticas = [{ texto = "exemplo.c1", de = "socialismo" },'
                ' { texto = "exemplo.c2", de = "socialismo" }]',
            ),
            "pelo menos 2 origens",
            id="criticas-de-uma-origem",
        ),
        pytest.param(
            _trocar(
                "criticas",
                'criticas = [{ texto = "exemplo.c1", de = "conservadorismo" },'
                ' { texto = "exemplo.c2", de = "outras" }]',
            ),
            "própria corrente",
            id="critica-da-propria-corrente",
        ),
        pytest.param(
            _trocar(
                "criticas",
                'criticas = [{ texto = "exemplo.c1", de = "anarquismo" },'
                ' { texto = "exemplo.c2", de = "outras" }]',
            ),
            "origem desconhecida",
            id="critica-de-origem-desconhecida",
        ),
        pytest.param(
            _trocar("criticas", 'criticas = [{ texto = "exemplo.c1" }, "exemplo.c2"]'),
            "exatamente as chaves",
            id="critica-sem-de",
        ),
        pytest.param(
            _trocar("fontes", 'fontes = [{ autor = "A", titulo = "T", ano = 2000 }]'),
            "fonte 1: a fonte precisa de 'editora' ou 'url'",
            id="fonte-invalida",
        ),
        pytest.param(_trocar("se", 'se = "exemplo.f"'), "lista de flags", id="se-texto"),
    ],
)
def test_ficha_fora_do_modelo_e_recusada(conteudo, trecho_da_mensagem):
    with pytest.raises(FichaInvalida, match=trecho_da_mensagem):
        Fichas.de_toml(conteudo)


def test_ficha_inexistente_levanta_keyerror_com_a_corrente():
    with pytest.raises(KeyError, match="socialismo"):
        Fichas.de_toml(ficha_toml("liberalismo"))["socialismo"]


# --- Desbloqueio ---------------------------------------------------------------------------


def todas() -> Fichas:
    # Escritas fora da ordem de propósito.
    return Fichas.de_toml("".join(ficha_toml(corrente) for corrente in reversed(CORRENTES)))


def test_fichas_ficam_na_ordem_fixa_das_correntes():
    assert list(todas()) == list(CORRENTES)


def test_ficha_aparece_so_com_a_flag_de_desbloqueio():
    fichas = todas()
    estado = EstadoJogo()
    assert fichas.desbloqueadas(estado) == ()
    estado.marcar_flag("exemplo.socialismo.desbloqueio")
    assert [f.corrente for f in fichas.desbloqueadas(estado)] == ["socialismo"]


def test_desbloqueadas_saem_na_ordem_fixa_mesmo_desbloqueando_em_outra_ordem():
    fichas = todas()
    estado = EstadoJogo()
    for corrente in reversed(CORRENTES):
        estado.marcar_flag(f"exemplo.{corrente}.desbloqueio")
    assert [f.corrente for f in fichas.desbloqueadas(estado)] == list(CORRENTES)


# --- Conteúdo ------------------------------------------------------------------------------


def test_ids_de_texto_seguem_a_ordem_do_modelo():
    ficha = Fichas.de_toml(ficha_toml("liberalismo"))["liberalismo"]
    assert ficha.ids_de_texto() == (
        "exemplo.liberalismo.ideia",
        "exemplo.liberalismo.valor_1",
        "exemplo.liberalismo.valor_2",
        "exemplo.liberalismo.estado",
        "exemplo.liberalismo.mercado",
        "exemplo.liberalismo.sociedade",
        "exemplo.liberalismo.origem",
        "exemplo.liberalismo.pensador",
        "exemplo.liberalismo.proposta",
        "exemplo.liberalismo.critica_1",
        "exemplo.liberalismo.critica_2",
        "exemplo.liberalismo.confusao",
        "exemplo.liberalismo.vertente_1",
        "exemplo.liberalismo.vertente_2",
    )


def test_catalogo_junta_textos_e_flags():
    fichas = todas()
    assert len(fichas.ids_de_texto()) == 14 * len(CORRENTES)
    assert fichas.flags_exigidas() == {f"exemplo.{c}.desbloqueio" for c in CORRENTES}


def test_exemplo_do_comentario_do_arquivo_e_valido():
    from importlib.resources import files

    linhas = (files("politicalizando.conteudo") / "fichas.toml").read_text("utf-8").splitlines()
    inicio = next(i for i, linha in enumerate(linhas) if linha.startswith("# Exemplo")) + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    assert list(Fichas.de_toml("\n".join(exemplo))) == ["liberalismo"]


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_fichas(), Fichas)
