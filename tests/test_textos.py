import dataclasses

import pytest

from politicalizando.conteudo import carregar_textos
from politicalizando.dominio.textos import Texto, TextoInvalido, Textos

# Textos de exemplo, neutros e provisórios: só existem nos testes.
EXEMPLO = """
[exemplo.guia.ola]
quem = "guia"
texto = "Olá. Este é um texto de exemplo."

[exemplo.aviso]
texto = "Um aviso sem ninguém falando."

[exemplo.guia.varias_linhas]
quem = "guia"
texto = '''
Primeira linha.
Segunda linha.'''
"""


def test_texto_com_quem_fala():
    textos = Textos.de_toml(EXEMPLO)
    assert textos["exemplo.guia.ola"] == Texto(
        id="exemplo.guia.ola", texto="Olá. Este é um texto de exemplo.", quem="guia"
    )


def test_texto_sem_quem_e_narracao_ou_interface():
    assert Textos.de_toml(EXEMPLO)["exemplo.aviso"].quem is None


def test_texto_de_varias_linhas():
    texto = Textos.de_toml(EXEMPLO)["exemplo.guia.varias_linhas"].texto
    assert texto == "Primeira linha.\nSegunda linha."


def test_tabelas_aninhadas_viram_ids_com_ponto():
    assert set(Textos.de_toml(EXEMPLO)) == {
        "exemplo.guia.ola",
        "exemplo.aviso",
        "exemplo.guia.varias_linhas",
    }


def test_id_de_um_trecho_so():
    assert Textos.de_toml('[ola]\ntexto = "Olá."')["ola"].texto == "Olá."


def test_arquivo_vazio_gera_catalogo_vazio():
    textos = Textos.de_toml("# só um comentário\n")
    assert len(textos) == 0
    assert list(textos) == []


@pytest.mark.parametrize(
    "conteudo",
    [
        pytest.param('[exemplo.ola\ntexto = "Olá."', id="sintaxe-quebrada"),
        pytest.param(
            '[exemplo.ola]\ntexto = "Olá."\n[exemplo.ola]\ntexto = "De novo."',
            id="tabela-duplicada",
        ),
        pytest.param('[exemplo.ola]\ntexto = "Olá."\ntexto = "De novo."', id="chave-duplicada"),
        pytest.param('[Exemplo.ola]\ntexto = "Olá."', id="id-com-maiuscula"),
        pytest.param('[exemplo."olá"]\ntexto = "Olá."', id="id-com-acento"),
        pytest.param('[exemplo.bom-dia]\ntexto = "Bom dia."', id="id-com-hifen"),
        pytest.param('["exemplo.ola"]\ntexto = "Olá."', id="chave-entre-aspas-com-ponto"),
        pytest.param('[exemplo.ola]\ntexto = ""', id="texto-vazio"),
        pytest.param('[exemplo.ola]\ntexto = "   "', id="texto-so-espacos"),
        pytest.param("[exemplo.ola]\ntexto = 3", id="texto-numero"),
        pytest.param('[exemplo.ola]\nquem = "Guia"\ntexto = "Olá."', id="quem-invalido"),
        pytest.param('[exemplo.ola]\nquem = 1\ntexto = "Olá."', id="quem-numero"),
        pytest.param('[exemplo.ola]\nqem = "guia"\ntexto = "Olá."', id="chave-extra"),
        pytest.param('[exemplo.ola]\nquem = "guia"', id="sem-texto"),
        pytest.param('[exemplo]\nversao = 1\n[exemplo.ola]\ntexto = "Olá."', id="valor-solto"),
        pytest.param('ola = "Olá."', id="valor-solto-na-raiz"),
        pytest.param(
            '[exemplo]\ntexto = "Pai."\n[exemplo.ola]\ntexto = "Filho."',
            id="id-prefixo-de-outro",
        ),
    ],
)
def test_formato_fora_do_padrao_e_recusado(conteudo):
    with pytest.raises(TextoInvalido):
        Textos.de_toml(conteudo)


def test_id_inexistente_levanta_keyerror_com_o_id():
    textos = Textos.de_toml(EXEMPLO)
    with pytest.raises(KeyError, match="exemplo.nao_existe"):
        textos["exemplo.nao_existe"]


def test_consulta_como_dicionario():
    textos = Textos.de_toml(EXEMPLO)
    assert "exemplo.aviso" in textos
    assert "exemplo" not in textos
    assert len(textos) == 3
    assert textos.get("exemplo.nao_existe") is None


def test_texto_e_imutavel():
    texto = Textos.de_toml(EXEMPLO)["exemplo.aviso"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        texto.texto = "Outro."


def test_arquivo_do_jogo_carrega_sem_erro():
    textos = carregar_textos()
    assert len(textos) > 0
    assert all(isinstance(texto, Texto) for texto in textos.values())
