import datetime

import pytest

from politicalizando.dominio.fontes import Fonte, ler_fonte

# Fontes fictícias, só para os testes.
LIVRO = {"autor": "Exemplo, Autor", "titulo": "Livro de exemplo", "ano": 1999, "editora": "Ed."}
SITE = {
    "autor": "Instituto Exemplo",
    "titulo": "Página de exemplo",
    "ano": 2024,
    "url": "https://exemplo.org/pagina",
    "acesso": datetime.date(2026, 10, 14),
}


def test_fonte_com_editora():
    assert ler_fonte(LIVRO, "teste") == Fonte(
        autor="Exemplo, Autor", titulo="Livro de exemplo", ano=1999, editora="Ed."
    )


def test_fonte_com_url_e_acesso():
    fonte = ler_fonte(SITE, "teste")
    assert fonte.url == "https://exemplo.org/pagina"
    assert fonte.acesso == datetime.date(2026, 10, 14)
    assert fonte.editora is None


def _com(base: dict, **mudancas) -> dict:
    dados = dict(base)
    for chave, valor in mudancas.items():
        if valor is None:
            dados.pop(chave, None)
        else:
            dados[chave] = valor
    return dados


@pytest.mark.parametrize(
    ("dados", "trecho_da_mensagem"),
    [
        pytest.param("Livro", "uma fonte é uma tabela", id="nao-e-tabela"),
        pytest.param(_com(LIVRO, autor=None), "falta a chave 'autor'", id="sem-autor"),
        pytest.param(_com(LIVRO, titulo=None), "falta a chave 'titulo'", id="sem-titulo"),
        pytest.param(_com(LIVRO, ano=None), "falta a chave 'ano'", id="sem-ano"),
        pytest.param(_com(LIVRO, autor="  "), "'autor' não vazio", id="autor-vazio"),
        pytest.param(_com(LIVRO, ano="1999"), "ano inválido", id="ano-texto"),
        pytest.param(_com(LIVRO, ano=True), "ano inválido", id="ano-booleano"),
        pytest.param(_com(LIVRO, ano=999), "ano fora", id="ano-antigo-demais"),
        pytest.param(_com(LIVRO, ano=2101), "ano fora", id="ano-futuro-demais"),
        pytest.param(_com(LIVRO, editora=None), "'editora' ou 'url'", id="sem-editora-nem-url"),
        pytest.param(_com(LIVRO, editora=""), "não pode ficar vazia", id="editora-vazia"),
        pytest.param(_com(SITE, url="http://exemplo.org"), "https://", id="url-sem-https"),
        pytest.param(_com(SITE, acesso=None), "data de 'acesso'", id="url-sem-acesso"),
        pytest.param(_com(SITE, acesso="2026-10-14"), "deveria ser uma data", id="acesso-texto"),
        pytest.param(
            _com(SITE, acesso=datetime.datetime(2026, 10, 14, 10, 0)),
            "deveria ser uma data",
            id="acesso-com-hora",
        ),
        pytest.param(_com(LIVRO, pagina=10), "chaves inesperadas", id="chave-extra"),
    ],
)
def test_fonte_fora_do_formato_e_recusada(dados, trecho_da_mensagem):
    with pytest.raises(ValueError, match=trecho_da_mensagem):
        ler_fonte(dados, "teste")


def test_mensagem_diz_onde_esta_o_erro():
    with pytest.raises(ValueError, match="^ficha 'x', fonte 2: "):
        ler_fonte(_com(LIVRO, ano=1), "ficha 'x', fonte 2")
