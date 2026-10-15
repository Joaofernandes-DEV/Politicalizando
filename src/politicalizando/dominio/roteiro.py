"""Roteiros em dados: sequências simples descritas em TOML e executadas pelo diretor (D11).

Cada lista é um roteiro, e o caminho dela é o ID; cada passo tem exatamente uma ação:

    [exemplo]
    apresentacao = [
      { fala = "exemplo.guia.ola" },
      { esperar = 0.5 },
      { marcar_flag = "exemplo.apresentou" },
    ]

Escolhas com ramos ficam nas árvores de diálogo; casos especiais ficam em Python. Os dois tipos
de roteiro têm a mesma forma de uso: `diretor.iniciar(sequencia.executar(estado))`.
"""

from __future__ import annotations

import tomllib
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass

from politicalizando.dominio.acoes import (
    AbrirTela,
    Acao,
    DarItem,
    Esperar,
    Fala,
    MarcarFlag,
    Roteiro,
    TrocarCena,
)
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id

# Chave do passo no TOML → ação criada a partir do valor.
_PASSOS: dict[str, Callable[[object], Acao]] = {
    "fala": Fala,
    "esperar": Esperar,
    "marcar_flag": MarcarFlag,
    "dar_item": DarItem,
    "trocar_cena": TrocarCena,
    "abrir_tela": AbrirTela,
}


class RoteiroInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de roteiros malformado: sintaxe, ID, passo ou valor fora do formato."""


@dataclass(frozen=True)
class Sequencia:
    id: str
    acoes: tuple[Acao, ...]

    def executar(self, estado: EstadoJogo) -> Roteiro:
        """Um gerador novo a cada chamada, pronto para o `Diretor`."""
        yield from self.acoes

    def ids_de_texto(self) -> set[str]:
        return {acao.id_texto for acao in self.acoes if isinstance(acao, Fala)}


class Roteiros(Mapping[str, Sequencia]):
    """Catálogo imutável de sequências, consultado pelo ID."""

    def __init__(self, sequencias: dict[str, Sequencia] | None = None) -> None:
        self._sequencias = dict(sequencias or {})

    def __getitem__(self, id_roteiro: str) -> Sequencia:
        try:
            return self._sequencias[id_roteiro]
        except KeyError:
            raise KeyError(f"roteiro inexistente: {id_roteiro!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._sequencias)

    def __len__(self) -> int:
        return len(self._sequencias)

    def ids_de_texto(self) -> set[str]:
        """Todos os IDs de texto usados pelas falas dos roteiros."""
        return set().union(*(sequencia.ids_de_texto() for sequencia in self.values()))

    @classmethod
    def de_toml(cls, conteudo: str) -> Roteiros:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise RoteiroInvalido(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Roteiros:
        """Achata as tabelas aninhadas em IDs com ponto e valida cada passo."""
        sequencias: dict[str, Sequencia] = {}
        _coletar(dados, (), sequencias)
        return cls(sequencias)


def _coletar(
    tabela: dict[str, object], caminho: tuple[str, ...], saida: dict[str, Sequencia]
) -> None:
    for chave, valor in tabela.items():
        trecho = (*caminho, chave)
        nome = ".".join(trecho)
        if "." in chave:
            raise RoteiroInvalido(f"ID inválido: {nome!r} (use tabelas aninhadas, não pontos)")
        try:
            validar_id(nome)
        except ValueError as erro:
            raise RoteiroInvalido(str(erro)) from erro
        if isinstance(valor, list):
            saida[nome] = _sequencia(nome, valor)
        elif isinstance(valor, dict):
            _coletar(valor, trecho, saida)
        else:
            raise RoteiroInvalido(f"valor solto em {nome!r}: um roteiro é uma lista de passos")


def _sequencia(id_roteiro: str, passos: list[object]) -> Sequencia:
    if not passos:
        raise RoteiroInvalido(f"o roteiro {id_roteiro!r} não tem passos")
    try:
        return Sequencia(id=id_roteiro, acoes=ler_passos(passos, repr(id_roteiro)))
    except ValueError as erro:
        raise RoteiroInvalido(str(erro)) from erro


def ler_passos(passos: object, onde: str) -> tuple[Acao, ...]:
    """Converte uma lista de passos do TOML em ações; também usada pelos nós de diálogo.

    Levanta `ValueError` com `onde` e o número do passo na mensagem.
    """
    if not isinstance(passos, list):
        raise ValueError(f"{onde}: 'passos' deveria ser uma lista")
    return tuple(_acao(f"{onde}, passo {numero}", passo) for numero, passo in enumerate(passos, 1))


def _acao(onde: str, passo: object) -> Acao:
    if not isinstance(passo, dict) or len(passo) != 1:
        raise ValueError(f"{onde}: cada passo é uma tabela com exatamente uma ação")
    ((chave, valor),) = passo.items()
    if chave == "escolha":
        raise ValueError(
            f"{onde}: escolhas não são passos; os ramos ficam nas opções das árvores de diálogo"
        )
    if chave not in _PASSOS:
        raise ValueError(f"{onde}: ação desconhecida {chave!r} (aceitas: {sorted(_PASSOS)})")
    try:
        return _PASSOS[chave](valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from erro
