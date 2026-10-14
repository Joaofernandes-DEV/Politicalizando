"""Textos do jogo por ID: quem fala e o que diz (briefing, seção 3).

Todo texto de tela fica nos dados (`conteudo/pt_BR/textos.toml`), nunca no código. Aqui ficam
só as regras do formato; a leitura do arquivo está em `conteudo/`.

No TOML, cada tabela com a chave `texto` é uma entrada, e o caminho dela é o ID:

    [titulo.frase]
    texto = "Pensar antes de escolher um lado."

`quem` é opcional e guarda o ID de quem fala; sem ele, o texto é narração ou interface.
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from politicalizando.dominio.estado_jogo import validar_id

_CHAVES_ENTRADA = frozenset({"texto", "quem"})


class TextoInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de textos malformado: sintaxe, ID, chave ou valor fora do formato."""


@dataclass(frozen=True)
class Texto:
    id: str
    texto: str
    quem: str | None = None


class Textos(Mapping[str, Texto]):
    """Catálogo imutável de textos, consultado pelo ID: `textos["titulo.frase"]`."""

    def __init__(self, entradas: dict[str, Texto] | None = None) -> None:
        self._entradas = dict(entradas or {})

    def __getitem__(self, id_texto: str) -> Texto:
        try:
            return self._entradas[id_texto]
        except KeyError:
            raise KeyError(f"texto inexistente: {id_texto!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._entradas)

    def __len__(self) -> int:
        return len(self._entradas)

    @classmethod
    def de_toml(cls, conteudo: str) -> Textos:
        """Lê o texto de um arquivo TOML; levanta `TextoInvalido` se algo não bate."""
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise TextoInvalido(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Textos:
        """Achata as tabelas aninhadas em IDs com ponto e valida cada entrada."""
        entradas: dict[str, Texto] = {}
        _coletar(dados, (), entradas)
        return cls(entradas)


def _coletar(tabela: dict[str, object], caminho: tuple[str, ...], saida: dict[str, Texto]) -> None:
    for chave, valor in tabela.items():
        trecho = (*caminho, chave)
        nome = ".".join(trecho)
        if "." in chave:
            raise TextoInvalido(f"ID inválido: {nome!r} (use tabelas aninhadas, não pontos)")
        try:
            validar_id(nome)
        except ValueError as erro:
            raise TextoInvalido(str(erro)) from erro
        if not isinstance(valor, dict):
            raise TextoInvalido(f"valor solto em {nome!r}: só tabelas de texto são aceitas")
        if "texto" in valor:
            saida[nome] = _entrada(nome, valor)
        elif any(not isinstance(item, dict) for item in valor.values()):
            raise TextoInvalido(f"{nome!r} tem valores, mas falta a chave 'texto'")
        else:
            _coletar(valor, trecho, saida)


def _entrada(id_texto: str, valor: dict[str, object]) -> Texto:
    extras = set(valor) - _CHAVES_ENTRADA
    if any(isinstance(valor[chave], dict) for chave in extras):
        raise TextoInvalido(f"{id_texto!r} é um texto e não pode ter outros IDs abaixo dele")
    if extras:
        raise TextoInvalido(f"chaves inesperadas em {id_texto!r}: {sorted(extras)}")
    texto = valor["texto"]
    if not isinstance(texto, str) or not texto.strip():
        raise TextoInvalido(f"{id_texto!r} precisa de um texto não vazio")
    quem = valor.get("quem")
    if quem is not None:
        try:
            validar_id(quem)
        except ValueError as erro:
            raise TextoInvalido(f"'quem' inválido em {id_texto!r}: {quem!r}") from erro
    return Texto(id=id_texto, texto=texto, quem=quem)
