import dataclasses

import pytest

from politicalizando.conteudo import carregar_roteiros
from politicalizando.dominio.acoes import DarItem, Esperar, Fala, MarcarFlag, TrocarCena
from politicalizando.dominio.diretor import Diretor
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.roteiro import RoteiroInvalido, Roteiros, Sequencia

# Roteiros de exemplo, neutros e provisórios: só existem nos testes.
EXEMPLO = """
[exemplo]
apresentacao = [
  { trocar_cena = "praca" },
  { fala = "exemplo.guia.ola" },
  { esperar = 0.5 },
  { marcar_flag = "exemplo.apresentou" },
  { dar_item = "caderno" },
  { fala = "exemplo.guia.tchau" },
]

[exemplo.guia]
pausa = [{ esperar = 2 }]
"""


def test_cada_passo_vira_a_acao_certa_na_ordem():
    sequencia = Roteiros.de_toml(EXEMPLO)["exemplo.apresentacao"]
    assert sequencia == Sequencia(
        id="exemplo.apresentacao",
        acoes=(
            TrocarCena("praca"),
            Fala("exemplo.guia.ola"),
            Esperar(0.5),
            MarcarFlag("exemplo.apresentou"),
            DarItem("caderno"),
            Fala("exemplo.guia.tchau"),
        ),
    )


def test_tabelas_aninhadas_viram_ids_com_ponto():
    assert set(Roteiros.de_toml(EXEMPLO)) == {"exemplo.apresentacao", "exemplo.guia.pausa"}


def test_chave_com_ponto_na_raiz_tambem_vira_id():
    roteiros = Roteiros.de_toml('exemplo.cena.entrada = [{ marcar_flag = "exemplo.entrou" }]')
    assert list(roteiros) == ["exemplo.cena.entrada"]


def test_esperar_aceita_inteiro():
    assert Roteiros.de_toml(EXEMPLO)["exemplo.guia.pausa"].acoes == (Esperar(2.0),)


def test_arquivo_sem_roteiros_gera_catalogo_vazio():
    assert len(Roteiros.de_toml("# só um comentário\n")) == 0


@pytest.mark.parametrize(
    ("conteudo", "trecho_da_mensagem"),
    [
        pytest.param("exemplo = [", "TOML inválido", id="sintaxe-quebrada"),
        pytest.param("Exemplo = [{ esperar = 1 }]", "ID inválido", id="id-com-maiuscula"),
        pytest.param('"exemplo.a" = [{ esperar = 1 }]', "ID inválido", id="chave-com-ponto"),
        pytest.param('exemplo = "fala"', "valor solto", id="valor-solto"),
        pytest.param("exemplo = []", "não tem passos", id="roteiro-vazio"),
        pytest.param('exemplo = ["exemplo.ola"]', "exatamente uma ação", id="passo-texto"),
        pytest.param("exemplo = [{}]", "exatamente uma ação", id="passo-vazio"),
        pytest.param(
            'exemplo = [{ fala = "exemplo.ola", esperar = 1 }]',
            "exatamente uma ação",
            id="passo-com-duas-acoes",
        ),
        pytest.param('exemplo = [{ falar = "exemplo.ola" }]', "desconhecida", id="acao-errada"),
        pytest.param(
            'exemplo = [{ escolha = ["exemplo.sim"] }]', "árvores de diálogo", id="escolha"
        ),
        pytest.param('exemplo = [{ fala = "Ola" }]', "passo 1", id="fala-id-invalido"),
        pytest.param(
            "exemplo = [{ esperar = 1 }, { esperar = -1 }]", "passo 2", id="espera-negativa"
        ),
        pytest.param("exemplo = [{ dar_item = 3 }]", "passo 1", id="item-numero"),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo, trecho_da_mensagem):
    with pytest.raises(RoteiroInvalido, match=trecho_da_mensagem):
        Roteiros.de_toml(conteudo)


def test_roteiro_inexistente_levanta_keyerror_com_o_id():
    with pytest.raises(KeyError, match="exemplo.nao_existe"):
        Roteiros.de_toml(EXEMPLO)["exemplo.nao_existe"]


def test_sequencia_e_imutavel():
    sequencia = Roteiros.de_toml(EXEMPLO)["exemplo.guia.pausa"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        sequencia.acoes = ()


def test_diretor_executa_a_sequencia_dos_dados_ate_o_fim():
    sequencia = Roteiros.de_toml(EXEMPLO)["exemplo.apresentacao"]
    estado = EstadoJogo()
    diretor = Diretor(estado)
    diretor.iniciar(sequencia.executar(estado))

    assert estado.cena_atual == "praca"
    assert diretor.acao_atual == Fala("exemplo.guia.ola")
    assert diretor.confirmar()
    diretor.atualizar(0.5)
    assert estado.tem_flag("exemplo.apresentou")
    assert estado.inventario == ("caderno",)
    assert diretor.acao_atual == Fala("exemplo.guia.tchau")
    assert diretor.confirmar()
    assert not diretor.ocupado


def test_sequencia_pode_rodar_de_novo():
    sequencia = Roteiros.de_toml(EXEMPLO)["exemplo.guia.pausa"]
    estado = EstadoJogo()
    diretor = Diretor(estado)
    for _ in range(2):
        diretor.iniciar(sequencia.executar(estado))
        assert diretor.acao_atual == Esperar(2)
        diretor.atualizar(2)
        assert not diretor.ocupado


def test_ids_de_texto_sao_os_das_falas():
    roteiros = Roteiros.de_toml(EXEMPLO)
    assert roteiros["exemplo.apresentacao"].ids_de_texto() == {
        "exemplo.guia.ola",
        "exemplo.guia.tchau",
    }
    assert roteiros["exemplo.guia.pausa"].ids_de_texto() == set()
    assert roteiros.ids_de_texto() == {"exemplo.guia.ola", "exemplo.guia.tchau"}


def test_catalogo_vazio_nao_usa_textos():
    assert Roteiros().ids_de_texto() == set()


def test_arquivo_do_jogo_carrega_sem_erro():
    assert isinstance(carregar_roteiros(), Roteiros)
