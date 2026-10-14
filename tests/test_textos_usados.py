"""Todo ID de texto usado existe em `textos.toml`, e nenhum texto de lá ficou órfão.

Os IDs vêm de duas fontes:

- do código: uma varredura com `ast` coleta, em `src/politicalizando/`, todo acesso
  `textos["id"]` (ou `algo.textos["id"]`) e as ações dos roteiros em Python, `Fala("id")` e
  `Escolha(("id_a", "id_b"))`;
- dos dados: as falas dos roteiros (`roteiros.toml`), as falas e opções dos diálogos
  (`dialogos.toml`) e os nomes de objeto, as falas em linha e as recusas das cenas
  (`cenas.toml`).
"""

import ast
import sys
from pathlib import Path

from politicalizando.conteudo import (
    carregar_cenas,
    carregar_dialogos,
    carregar_roteiros,
    carregar_textos,
)
from politicalizando.dominio.cenas import Cenas
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.roteiro import Roteiros

PASTA_CODIGO = Path(__file__).resolve().parents[1] / "src" / "politicalizando"

# Comentário que marca um uso de texto cujos IDs vêm dos dados, não do código.
MARCA_DADOS = "# ids-de-texto: dados"


def _e_catalogo_de_textos(no: ast.expr) -> bool:
    return (isinstance(no, ast.Name) and no.id == "textos") or (
        isinstance(no, ast.Attribute) and no.attr == "textos"
    )


def _texto_literal(no: ast.expr | None) -> str | None:
    if isinstance(no, ast.Constant) and isinstance(no.value, str):
        return no.value
    return None


def _nome_chamado(chamada: ast.Call) -> str | None:
    if isinstance(chamada.func, ast.Name):
        return chamada.func.id
    if isinstance(chamada.func, ast.Attribute):
        return chamada.func.attr
    return None


def _argumento(chamada: ast.Call, nome: str) -> ast.expr | None:
    """O primeiro argumento da chamada, posicional ou pelo nome."""
    if chamada.args:
        return chamada.args[0]
    return next((kw.value for kw in chamada.keywords if kw.arg == nome), None)


def _ids_da_acao(chamada: ast.Call) -> list[str | None] | None:
    """IDs de texto de `Fala(...)` ou `Escolha(...)`; `None` na lista marca um não literal."""
    match _nome_chamado(chamada):
        case "Fala":
            return [_texto_literal(_argumento(chamada, "id_texto"))]
        case "Escolha":
            opcoes = _argumento(chamada, "opcoes")
            if isinstance(opcoes, ast.Tuple | ast.List):
                return [_texto_literal(opcao) for opcao in opcoes.elts]
            return [None]
    return None


def ids_no_codigo(fonte: str, nome_arquivo: str = "<codigo>") -> tuple[set[str], list[str]]:
    """IDs de texto usados no código e a lista de usos sem ID literal.

    Um uso marcado com `MARCA_DADOS` (na mesma linha ou na de cima) é ignorado: os IDs vêm dos
    dados, que já são conferidos pelo caminho dos dados (ex.: o motor de diálogos).
    """
    ids: set[str] = set()
    problemas: list[str] = []
    linhas = fonte.splitlines()
    for no in ast.walk(ast.parse(fonte, filename=nome_arquivo)):
        if not isinstance(no, ast.Subscript | ast.Call):
            continue
        if any(MARCA_DADOS in linha for linha in linhas[max(no.lineno - 2, 0) : no.lineno]):
            continue
        if isinstance(no, ast.Subscript) and _e_catalogo_de_textos(no.value):
            achados, onde = [_texto_literal(no.slice)], "textos[...]"
        elif isinstance(no, ast.Call) and (achados := _ids_da_acao(no)) is not None:
            onde = f"{_nome_chamado(no)}(...)"
        else:
            continue
        ids.update(id_texto for id_texto in achados if id_texto is not None)
        if None in achados:
            problemas.append(f"{nome_arquivo}:{no.lineno}: use um ID literal em {onde}")
    return ids, problemas


def ids_usados() -> tuple[set[str], list[str]]:
    ids: set[str] = set()
    problemas: list[str] = []
    for arquivo in sorted(PASTA_CODIGO.rglob("*.py")):
        nome = arquivo.relative_to(PASTA_CODIGO).as_posix()
        achados, erros = ids_no_codigo(arquivo.read_text(encoding="utf-8"), nome)
        ids |= achados
        problemas += erros
    ids |= carregar_roteiros().ids_de_texto()
    ids |= carregar_dialogos().ids_de_texto()
    ids |= carregar_cenas().ids_de_texto()
    return ids, problemas


def test_varredura_acha_os_acessos_literais():
    fonte = 'a = textos["um.id"]\nb = self.jogo.textos["outro.id"].texto\nc = outro["x"]\n'
    assert ids_no_codigo(fonte) == ({"um.id", "outro.id"}, [])


def test_varredura_acusa_acesso_sem_id_literal():
    ids, problemas = ids_no_codigo("chave = 'um.id'\nx = textos[chave]\n", "tela.py")
    assert ids == set()
    assert problemas == ["tela.py:2: use um ID literal em textos[...]"]


def test_varredura_acha_os_ids_das_acoes():
    fonte = (
        'yield Fala("exemplo.ola")\n'
        'yield acoes.Fala(id_texto="exemplo.tchau")\n'
        'yield Escolha(("exemplo.sim", "exemplo.nao"))\n'
        'yield Escolha(opcoes=["exemplo.talvez"])\n'
    )
    assert ids_no_codigo(fonte) == (
        {"exemplo.ola", "exemplo.tchau", "exemplo.sim", "exemplo.nao", "exemplo.talvez"},
        [],
    )


def test_varredura_acusa_acao_sem_id_literal():
    fonte = 'yield Fala(id_texto)\nyield Escolha(opcoes)\nyield Escolha(("exemplo.sim", x))\n'
    ids, problemas = ids_no_codigo(fonte, "roteiro.py")
    assert ids == {"exemplo.sim"}
    assert problemas == [
        "roteiro.py:1: use um ID literal em Fala(...)",
        "roteiro.py:2: use um ID literal em Escolha(...)",
        "roteiro.py:3: use um ID literal em Escolha(...)",
    ]


def test_varredura_aceita_uso_marcado_como_vindo_dos_dados():
    fonte = (
        "# ids-de-texto: dados\n"
        "yield Escolha(opcoes)\n"
        "x = textos[chave]  # ids-de-texto: dados\n"
        "\n"
        "yield Fala(id_texto)\n"
    )
    ids, problemas = ids_no_codigo(fonte, "motor.py")
    assert ids == set()
    assert problemas == ["motor.py:5: use um ID literal em Fala(...)"]


def test_ids_usados_inclui_as_falas_dos_roteiros(monkeypatch):
    roteiros = Roteiros.de_toml('exemplo.cena = [{ fala = "exemplo.so_no_roteiro" }]')
    monkeypatch.setattr(sys.modules[__name__], "carregar_roteiros", lambda: roteiros)
    ids, _ = ids_usados()
    assert "exemplo.so_no_roteiro" in ids


def test_ids_usados_inclui_as_falas_e_opcoes_dos_dialogos(monkeypatch):
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\n'
        'passos = [{ fala = "exemplo.so_no_dialogo" }]\n'
        'opcoes = [{ id = "x", texto = "exemplo.opcao_do_dialogo", vai_para = "fim" }]'
    )
    monkeypatch.setattr(sys.modules[__name__], "carregar_dialogos", lambda: dialogos)
    ids, _ = ids_usados()
    assert {"exemplo.so_no_dialogo", "exemplo.opcao_do_dialogo"} <= ids


def test_ids_usados_inclui_os_textos_das_cenas(monkeypatch):
    cenas = Cenas.de_toml(
        """
[recusas]
olhar = ["exemplo.r_olhar"]
usar = ["exemplo.r_usar"]
falar = ["exemplo.r_falar"]

[cenas.sala]
objetos = [
  { id = "a", nome = "exemplo.nome", area = [0, 0, 1, 1], olhar = [{ fala = "exemplo.olhar" }] },
]
"""
    )
    monkeypatch.setattr(sys.modules[__name__], "carregar_cenas", lambda: cenas)
    ids, _ = ids_usados()
    assert {"exemplo.nome", "exemplo.olhar", "exemplo.r_olhar", "exemplo.r_falar"} <= ids


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
