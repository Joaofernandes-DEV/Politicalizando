from importlib.resources import files

import pytest

from politicalizando.conteudo import carregar_dialogos
from politicalizando.dominio.acoes import DarItem, Escolha, Fala, MarcarFlag
from politicalizando.dominio.correntes import CORRENTES, validar_corrente
from politicalizando.dominio.dialogo import DialogoInvalido, Dialogos
from politicalizando.dominio.diretor import Diretor
from politicalizando.dominio.estado_jogo import EstadoJogo

# Diálogo de exemplo, neutro e provisório: só existe nos testes. Usa as duas formas de escrever
# opções (lista de tabelas e lista em linha).
EXEMPLO = """
[exemplo.guia]
inicio = "ola"

[exemplo.guia.nos.ola]
passos = [{ fala = "exemplo.guia.ola" }]

[[exemplo.guia.nos.ola.opcoes]]
id = "pergunta"
texto = "exemplo.guia.pergunta"
vai_para = "resposta"
uso_unico = true

[[exemplo.guia.nos.ola.opcoes]]
id = "detalhe"
texto = "exemplo.guia.detalhe"
vai_para = "detalhe"
se = ["exemplo.guia.pergunta"]

[[exemplo.guia.nos.ola.opcoes]]
id = "tchau"
texto = "exemplo.guia.tchau"
vai_para = "fim"

[exemplo.guia.nos.resposta]
passos = [{ fala = "exemplo.guia.resposta" }]
vai_para = "ola"

[exemplo.guia.nos.detalhe]
passos = [{ fala = "exemplo.guia.detalhe_resposta" }, { dar_item = "folheto" }]
opcoes = [
  { id = "voltar", texto = "exemplo.guia.voltar", vai_para = "ola" },
  { id = "novo", texto = "exemplo.guia.novo", vai_para = "fim", se_nao = ["exemplo.guia.voltar"] },
]
"""

OLA = Fala("exemplo.guia.ola")


def conversa(conteudo: str = EXEMPLO, id_dialogo: str = "exemplo.guia", estado=None):
    estado = estado or EstadoJogo()
    diretor = Diretor(estado)
    diretor.iniciar(Dialogos.de_toml(conteudo)[id_dialogo].executar(estado))
    return diretor, estado


def opcoes_na_tela(diretor: Diretor) -> tuple[str, ...]:
    assert isinstance(diretor.acao_atual, Escolha)
    return diretor.acao_atual.opcoes


# --- Formato -----------------------------------------------------------------------------


def test_carrega_o_dialogo_com_nos_e_opcoes():
    dialogo = Dialogos.de_toml(EXEMPLO)["exemplo.guia"]
    assert dialogo.inicio == "ola"
    assert set(dialogo.nos) == {"ola", "resposta", "detalhe"}
    assert dialogo.corrente is None

    pergunta, detalhe, tchau = dialogo.nos["ola"].opcoes
    assert (pergunta.id, pergunta.texto, pergunta.vai_para) == (
        "pergunta",
        "exemplo.guia.pergunta",
        "resposta",
    )
    assert pergunta.flag == "exemplo.guia.pergunta"
    assert pergunta.uso_unico
    assert detalhe.se == {"exemplo.guia.pergunta"}
    assert not tchau.uso_unico
    assert tchau.se == frozenset()
    assert tchau.se_nao == frozenset()
    assert dialogo.nos["resposta"].vai_para == "ola"
    assert dialogo.nos["detalhe"].passos == (
        Fala("exemplo.guia.detalhe_resposta"),
        DarItem("folheto"),
    )


@pytest.mark.parametrize("corrente", CORRENTES)
def test_dialogo_aceita_a_marcacao_de_corrente(corrente):
    conteudo = f'[exemplo.guia]\ninicio = "a"\ncorrente = "{corrente}"\n'
    conteudo += '[exemplo.guia.nos.a]\npassos = [{ fala = "exemplo.ola" }]\n'
    assert Dialogos.de_toml(conteudo)["exemplo.guia"].corrente == corrente


def test_as_quatro_correntes_da_v1():
    assert CORRENTES == ("liberalismo", "conservadorismo", "socialismo", "social_democracia")
    with pytest.raises(ValueError):
        validar_corrente("anarquismo")


def test_arquivo_sem_dialogos_gera_catalogo_vazio():
    assert len(Dialogos.de_toml("# só um comentário\n")) == 0


def _dialogo(nos: str, cabecalho: str = 'inicio = "a"') -> str:
    return f"[exemplo.guia]\n{cabecalho}\n{nos}"


NO_A_FIM = '[exemplo.guia.nos.a]\npassos = [{ fala = "exemplo.ola" }]\n'


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("[exemplo.guia\n", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param('exemplo = "x"', "valor solto", id="valor-solto"),
        pytest.param(_dialogo(NO_A_FIM, 'inicio = "Ola"'), "nome inválido", id="inicio-invalido"),
        pytest.param(_dialogo(NO_A_FIM, 'inicio = "b"'), "início 'b' não existe", id="sem-inicio"),
        pytest.param(_dialogo(""), "pelo menos um nó", id="sem-nos"),
        pytest.param(
            _dialogo(NO_A_FIM, 'inicio = "a"\ncorrente = "anarquismo"'),
            "corrente desconhecida",
            id="corrente-invalida",
        ),
        pytest.param(
            _dialogo(NO_A_FIM, 'inicio = "a"\nquem = "guia"'),
            "chaves inesperadas",
            id="chave-extra",
        ),
        pytest.param(_dialogo("[exemplo.guia.nos.a]\n"), "nó vazio", id="no-vazio"),
        pytest.param(
            _dialogo("[exemplo.guia.nos.a]\nvai_para = 'fim'\nopcoes = []"),
            "não os dois",
            id="opcoes-e-vai-para",
        ),
        pytest.param(
            _dialogo("[exemplo.guia.nos.a]\nopcoes = []"),
            "pelo menos uma opção",
            id="opcoes-vazias",
        ),
        pytest.param(
            _dialogo('[exemplo.guia.nos.a]\npassos = [{ escolha = ["exemplo.x"] }]'),
            "nó 'a', passo 1",
            id="escolha-nos-passos",
        ),
        pytest.param(
            _dialogo('[exemplo.guia.nos.a]\npassos = [{ fala = "Ola" }]'),
            "nó 'a', passo 1",
            id="passo-invalido",
        ),
        pytest.param(
            _dialogo(NO_A_FIM + "[exemplo.guia.nos.fim]\npassos = [{ esperar = 1 }]"),
            "reservado",
            id="no-chamado-fim",
        ),
        pytest.param(
            _dialogo(NO_A_FIM + 'vai_para = "b"'),
            "destino 'b' não existe",
            id="destino-inexistente",
        ),
        pytest.param(
            _dialogo(NO_A_FIM + "[exemplo.guia.nos.b]\npassos = [{ esperar = 1 }]"),
            "nunca são alcançados",
            id="no-orfao",
        ),
        pytest.param(
            _dialogo(
                NO_A_FIM
                + 'vai_para = "b"\n[exemplo.guia.nos.b]\npassos = [{ esperar = 1 }]\nvai_para = "a"'
            ),
            "laço sem escolha",
            id="laco-sem-escolha",
        ),
        pytest.param(
            _dialogo('[exemplo.guia.nos.a]\nopcoes = [{ id = "x", vai_para = "fim" }]'),
            "falta a chave 'texto'",
            id="opcao-sem-texto",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x.y", texto = "exemplo.x", vai_para = "fim" }]'
            ),
            "nome inválido",
            id="opcao-id-com-ponto",
        ),
        pytest.param(
            _dialogo(
                '[exemplo.guia.nos.a]\nopcoes = [{ id = "x", texto = "Ola", vai_para = "fim" }]'
            ),
            "opção 1: texto",
            id="opcao-texto-invalido",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x", texto = "exemplo.x", vai_para = "fim", uso_unico = "sim" }]'
            ),
            "uso_unico",
            id="uso-unico-texto",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x", texto = "exemplo.x", vai_para = "fim", se = "exemplo.f" }]'
            ),
            "lista de flags",
            id="se-texto",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x", texto = "exemplo.x", vai_para = "fim", se_nao = ["Flag"] }]'
            ),
            "se_nao",
            id="se-nao-flag-invalida",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x", texto = "exemplo.x", vai_para = "fim", pontos = 1 }]'
            ),
            "chaves inesperadas",
            id="opcao-chave-extra",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x", texto = "exemplo.x", vai_para = "fim" },'
                '{ id = "y", texto = "exemplo.x", vai_para = "fim" }]'
            ),
            "mesmo texto",
            id="texto-repetido-no-no",
        ),
        pytest.param(
            _dialogo(
                "[exemplo.guia.nos.a]\nopcoes = ["
                '{ id = "x", texto = "exemplo.x", vai_para = "b" }]\n'
                "[exemplo.guia.nos.b]\nopcoes = ["
                '{ id = "x", texto = "exemplo.y", vai_para = "fim" }]'
            ),
            "repetidos",
            id="id-de-opcao-repetido",
        ),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(DialogoInvalido, match=trecho_da_mensagem):
        Dialogos.de_toml(conteudo)


def test_dialogo_inexistente_levanta_keyerror_com_o_id():
    with pytest.raises(KeyError, match="exemplo.nao_existe"):
        Dialogos.de_toml(EXEMPLO)["exemplo.nao_existe"]


# --- Execução ----------------------------------------------------------------------------


def test_mostra_as_falas_e_depois_so_as_opcoes_visiveis():
    diretor, _ = conversa()
    assert diretor.acao_atual == OLA
    diretor.confirmar()
    # "detalhe" só aparece depois da pergunta (se = [...]).
    assert opcoes_na_tela(diretor) == ("exemplo.guia.pergunta", "exemplo.guia.tchau")


def test_escolher_marca_a_flag_da_opcao_e_vai_ao_destino():
    diretor, estado = conversa()
    diretor.confirmar()
    diretor.escolher(0)
    assert estado.tem_flag("exemplo.guia.pergunta")
    assert diretor.acao_atual == Fala("exemplo.guia.resposta")


def test_vai_para_volta_ao_inicio_e_uso_unico_some():
    diretor, _ = conversa()
    diretor.confirmar()
    diretor.escolher(0)
    diretor.confirmar()
    assert diretor.acao_atual == OLA
    diretor.confirmar()
    assert opcoes_na_tela(diretor) == ("exemplo.guia.detalhe", "exemplo.guia.tchau")


def test_uso_unico_continua_escondido_numa_conversa_nova():
    primeira, estado = conversa()
    primeira.confirmar()
    primeira.escolher(0)

    segunda, _ = conversa(estado=estado)
    segunda.confirmar()
    assert "exemplo.guia.pergunta" not in opcoes_na_tela(segunda)


def test_passos_do_no_aplicam_os_efeitos():
    estado = EstadoJogo()
    estado.marcar_flag("exemplo.guia.pergunta")
    diretor, _ = conversa(estado=estado)
    diretor.confirmar()
    diretor.escolher(0)  # detalhe
    assert diretor.acao_atual == Fala("exemplo.guia.detalhe_resposta")
    diretor.confirmar()
    assert estado.inventario == ("folheto",)


def test_se_nao_esconde_a_opcao():
    estado = EstadoJogo()
    estado.marcar_flag("exemplo.guia.pergunta")
    diretor, _ = conversa(estado=estado)
    diretor.confirmar()
    diretor.escolher(0)  # detalhe
    diretor.confirmar()
    assert opcoes_na_tela(diretor) == ("exemplo.guia.voltar", "exemplo.guia.novo")
    diretor.escolher(0)  # voltar: marca exemplo.guia.voltar
    diretor.confirmar()
    diretor.escolher(0)  # detalhe de novo
    diretor.confirmar()
    assert opcoes_na_tela(diretor) == ("exemplo.guia.voltar",)


def test_fim_encerra_o_dialogo():
    diretor, estado = conversa()
    diretor.confirmar()
    diretor.escolher(1)  # tchau
    assert estado.tem_flag("exemplo.guia.tchau")
    assert not diretor.ocupado


def test_no_sem_saida_encerra_o_dialogo():
    diretor, _ = conversa(_dialogo(NO_A_FIM))
    assert diretor.acao_atual == Fala("exemplo.ola")
    diretor.confirmar()
    assert not diretor.ocupado


def test_todas_as_opcoes_escondidas_encerram_o_dialogo():
    conteudo = _dialogo(
        NO_A_FIM
        + 'opcoes = [{ id = "x", texto = "exemplo.x", vai_para = "fim", uso_unico = true }]'
    )
    estado = EstadoJogo()
    estado.marcar_flag("exemplo.guia.x")
    diretor, _ = conversa(conteudo, estado=estado)
    diretor.confirmar()
    assert not diretor.ocupado


def test_vai_para_encadeia_nos_sem_escolha():
    conteudo = _dialogo(
        NO_A_FIM + 'vai_para = "b"\n[exemplo.guia.nos.b]\npassos = [{ fala = "exemplo.b" }]'
    )
    diretor, _ = conversa(conteudo)
    diretor.confirmar()
    assert diretor.acao_atual == Fala("exemplo.b")
    diretor.confirmar()
    assert not diretor.ocupado


def test_dialogo_pode_rodar_de_novo():
    dialogo = Dialogos.de_toml(EXEMPLO)["exemplo.guia"]
    estado = EstadoJogo()
    diretor = Diretor(estado)
    for _ in range(2):
        diretor.iniciar(dialogo.executar(estado))
        diretor.confirmar()
        diretor.escolher(len(opcoes_na_tela(diretor)) - 1)  # tchau
        assert not diretor.ocupado


# --- Conteúdo ----------------------------------------------------------------------------


def test_ids_de_texto_sao_as_falas_e_as_opcoes():
    assert Dialogos.de_toml(EXEMPLO).ids_de_texto() == {
        "exemplo.guia.ola",
        "exemplo.guia.pergunta",
        "exemplo.guia.detalhe",
        "exemplo.guia.tchau",
        "exemplo.guia.resposta",
        "exemplo.guia.detalhe_resposta",
        "exemplo.guia.voltar",
        "exemplo.guia.novo",
    }


def test_flags_exigidas_e_marcadas():
    dialogos = Dialogos.de_toml(EXEMPLO)
    assert dialogos.flags_exigidas() == {"exemplo.guia.pergunta", "exemplo.guia.voltar"}
    assert dialogos.flags_marcadas() == {
        "exemplo.guia.pergunta",
        "exemplo.guia.detalhe",
        "exemplo.guia.tchau",
        "exemplo.guia.voltar",
        "exemplo.guia.novo",
    }
    marcando = _dialogo('[exemplo.guia.nos.a]\npassos = [{ marcar_flag = "exemplo.ouviu" }]')
    assert Dialogos.de_toml(marcando).flags_marcadas() == {"exemplo.ouviu"}


def test_nenhum_dado_de_dialogo_mede_alinhamento():
    # E1: as únicas flags que um diálogo cria são as de "perguntou" das opções e as dos passos;
    # a marcação de corrente fica no diálogo e não vira flag.
    conteudo = _dialogo(
        '[exemplo.guia.nos.a]\nopcoes = [{ id = "x", texto = "exemplo.x", vai_para = "fim" }]',
        'inicio = "a"\ncorrente = "socialismo"',
    )
    dialogo = Dialogos.de_toml(conteudo)["exemplo.guia"]
    assert dialogo.flags_marcadas() == {"exemplo.guia.x"}
    assert not any("socialismo" in flag for flag in dialogo.flags_marcadas())


def test_exemplo_do_comentario_do_arquivo_e_valido():
    linhas = (files("politicalizando.conteudo") / "dialogos.toml").read_text("utf-8").splitlines()
    inicio = linhas.index("# Exemplo:") + 1
    exemplo = []
    for linha in linhas[inicio:]:
        if linha == "#":
            exemplo.append("")
        elif linha.startswith("#   "):
            exemplo.append(linha[4:])
        else:
            break
    dialogos = Dialogos.de_toml("\n".join(exemplo))
    assert list(dialogos) == ["biblioteca.bibliotecaria"]


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_dialogos(), Dialogos)


def test_marcar_flag_da_opcao_e_uma_acao_comum():
    # O diálogo usa só as ações que o diretor já conhece.
    dialogo = Dialogos.de_toml(EXEMPLO)["exemplo.guia"]
    estado = EstadoJogo()
    roteiro = dialogo.executar(estado)
    assert next(roteiro) == OLA
    assert isinstance(roteiro.send(None), Escolha)
    assert roteiro.send(1) == MarcarFlag("exemplo.guia.tchau")
