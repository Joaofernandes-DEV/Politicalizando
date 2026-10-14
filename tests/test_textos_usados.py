"""Todo ID de texto usado existe em `textos.toml`, e nenhum texto de lá ficou órfão.

Hoje os IDs vêm só do código: uma varredura com `ast` coleta todo acesso `textos["id"]` (ou
`algo.textos["id"]`) em `src/politicalizando/`. Quando os roteiros, diálogos e cenas chegarem,
cada tipo carregado dos dados expõe os IDs que usa, e `ids_usados` passa a juntá-los aqui.
"""

import ast
from pathlib import Path

from politicalizando.conteudo import carregar_textos

PASTA_CODIGO = Path(__file__).resolve().parents[1] / "src" / "politicalizando"


def _e_catalogo_de_textos(no: ast.expr) -> bool:
    return (isinstance(no, ast.Name) and no.id == "textos") or (
        isinstance(no, ast.Attribute) and no.attr == "textos"
    )


def ids_no_codigo(fonte: str, nome_arquivo: str = "<codigo>") -> tuple[set[str], list[str]]:
    """IDs acessados como `textos["id"]` e a lista de acessos sem ID literal."""
    ids: set[str] = set()
    problemas: list[str] = []
    for no in ast.walk(ast.parse(fonte, filename=nome_arquivo)):
        if isinstance(no, ast.Subscript) and _e_catalogo_de_textos(no.value):
            if isinstance(no.slice, ast.Constant) and isinstance(no.slice.value, str):
                ids.add(no.slice.value)
            else:
                problemas.append(f"{nome_arquivo}:{no.lineno}: use um ID literal em textos[...]")
    return ids, problemas


def ids_usados() -> tuple[set[str], list[str]]:
    ids: set[str] = set()
    problemas: list[str] = []
    for arquivo in sorted(PASTA_CODIGO.rglob("*.py")):
        nome = arquivo.relative_to(PASTA_CODIGO).as_posix()
        achados, erros = ids_no_codigo(arquivo.read_text(encoding="utf-8"), nome)
        ids |= achados
        problemas += erros
    return ids, problemas


def test_varredura_acha_os_acessos_literais():
    fonte = 'a = textos["um.id"]\nb = self.jogo.textos["outro.id"].texto\nc = outro["x"]\n'
    assert ids_no_codigo(fonte) == ({"um.id", "outro.id"}, [])


def test_varredura_acusa_acesso_sem_id_literal():
    ids, problemas = ids_no_codigo("chave = 'um.id'\nx = textos[chave]\n", "tela.py")
    assert ids == set()
    assert problemas == ["tela.py:2: use um ID literal em textos[...]"]


def test_codigo_so_acessa_textos_com_id_literal():
    _, problemas = ids_usados()
    assert problemas == []


def test_todo_id_usado_existe():
    ids, _ = ids_usados()
    assert ids, "nenhum uso de texto encontrado: a varredura parou de funcionar?"
    assert sorted(ids - set(carregar_textos())) == []


def test_nenhum_texto_orfao():
    ids, _ = ids_usados()
    assert sorted(set(carregar_textos()) - ids) == []
