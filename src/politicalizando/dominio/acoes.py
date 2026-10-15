"""Ações dos roteiros: o que uma sequência pede ao jogo (D11, briefing seção 3).

Um roteiro é um gerador que recebe o `EstadoJogo`, lê o estado diretamente e produz ações
com `yield`. A resposta de uma `Escolha` volta como valor do `yield`:

    def apresentacao(estado: EstadoJogo) -> Roteiro:
        yield Fala("exemplo.guia.ola")
        resposta = yield Escolha(("exemplo.guia.sim", "exemplo.guia.nao"))
        if resposta == 0:
            yield MarcarFlag("exemplo.aceitou")

`Fala`, `Esperar`, `Escolha` e `AbrirTela` esperam o jogador ou o tempo; `MarcarFlag`, `DarItem`
e `TrocarCena` mudam o estado na hora. Quem executa é o `Diretor`.
"""

from __future__ import annotations

import math
from collections.abc import Generator
from dataclasses import dataclass

from politicalizando.dominio.estado_jogo import validar_id


@dataclass(frozen=True)
class Fala:
    """Mostra um texto do `textos.toml` e espera o jogador confirmar. Quem fala vem do texto."""

    id_texto: str

    def __post_init__(self) -> None:
        validar_id(self.id_texto)


@dataclass(frozen=True)
class Escolha:
    """Oferece opções (IDs de texto) e devolve ao roteiro o índice escolhido."""

    opcoes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.opcoes, tuple | list):
            raise ValueError(f"as opções deveriam ser uma tupla de IDs: {self.opcoes!r}")
        opcoes = tuple(validar_id(opcao) for opcao in self.opcoes)
        if not opcoes:
            raise ValueError("uma escolha precisa de pelo menos uma opção")
        if len(set(opcoes)) != len(opcoes):
            raise ValueError(f"opções repetidas: {opcoes!r}")
        object.__setattr__(self, "opcoes", opcoes)


@dataclass(frozen=True)
class Esperar:
    """Pausa a sequência por alguns segundos."""

    segundos: float

    def __post_init__(self) -> None:
        segundos = self.segundos
        if isinstance(segundos, bool) or not isinstance(segundos, int | float):
            raise ValueError(f"tempo inválido: {segundos!r}")
        if not math.isfinite(segundos) or segundos <= 0:
            raise ValueError(f"o tempo de espera precisa ser positivo: {segundos!r}")
        object.__setattr__(self, "segundos", float(segundos))


@dataclass(frozen=True)
class MarcarFlag:
    flag: str

    def __post_init__(self) -> None:
        validar_id(self.flag)


@dataclass(frozen=True)
class DarItem:
    item: str

    def __post_init__(self) -> None:
        validar_id(self.item)


@dataclass(frozen=True)
class TrocarCena:
    """Muda a cena atual; o `Jogo` percebe a mudança e troca a tela."""

    cena: str

    def __post_init__(self) -> None:
        validar_id(self.cena)


# Telas que um roteiro pode abrir; cada uma é desenhada por um estado do jogo.
TELAS = ("comparacao", "materia")


@dataclass(frozen=True)
class AbrirTela:
    """Abre uma tela (ex.: a comparação de propostas) e espera o jogador fechá-la."""

    tela: str

    def __post_init__(self) -> None:
        if self.tela not in TELAS:
            raise ValueError(f"tela desconhecida: {self.tela!r} (aceitas: {', '.join(TELAS)})")


Acao = Fala | Escolha | Esperar | MarcarFlag | DarItem | TrocarCena | AbrirTela

# Ações que param a sequência até o jogador (ou o tempo) responder.
AcaoDeEspera = Fala | Escolha | Esperar | AbrirTela

# Recebe `None` depois de cada ação e o índice escolhido depois de uma `Escolha`.
Roteiro = Generator[Acao, int | None, None]
