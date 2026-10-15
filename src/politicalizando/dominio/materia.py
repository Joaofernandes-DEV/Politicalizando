"""A matéria do fechamento e a avaliação dela (J7, E1, E2).

Formato de `conteudo/materia.toml` (os textos ficam no `textos.toml`, por ID):

    [pecas.biblioteca.horario]
    tipo = "fato"
    texto = "materia.biblioteca.horario"
    se = ["praca.cartaz.checou"]
    fonte_se = ["praca.cartaz.acertou"]

    [pecas.biblioteca.visao_a]
    tipo = "opiniao"
    texto = "materia.biblioteca.visao_a"
    de = "biblioteca.bibliotecaria"
    corrente = "liberalismo"
    se = ["biblioteca.bibliotecaria.posicao"]

Cada tabela de `pecas` com `tipo` é uma peça, e o caminho dela é o ID. A peça fica disponível
quando as flags de `se` estão marcadas. O jogador monta a matéria escolhendo peças e, em cada
fato ou opinião, se vai **citar**: num fato, mostrar a fonte (só quando as flags de `fonte_se`
estão marcadas); numa opinião, dizer quem disse (`de`). Uma manipulação é uma armadilha:
incluí-la conta como um fato sem fonte, e ela nunca é "citada".

A avaliação tem três critérios, cada um com três níveis (0 a 2), e a nota total vai de 0 a 6:

- fatos com fonte: fatos citados ÷ (fatos + manipulações incluídas);
- opiniões atribuídas: opiniões citadas ÷ opiniões incluídas;
- visões com justiça: as correntes ouvidas aparecem na matéria de forma equilibrada.

Ela lê o estado só pelas flags de investigação e trata as correntes apenas por contagem, sem
nunca citar uma pelo nome: trocar as correntes de lugar não muda a nota (E2). Não há rótulo, e
a posição da matéria nunca é medida (E1).

O jogador pode entregar e reescrever quantas vezes quiser; `publicar` avalia a versão final e
marca `materia.publicou`, que encerra o capítulo.
"""

from __future__ import annotations

import tomllib
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from enum import IntEnum, StrEnum

from politicalizando.dominio.correntes import validar_corrente
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id

FLAG_PUBLICOU = "materia.publicou"
MINIMO_DE_CORRENTES = 2
DIFERENCA_MAXIMA_ENTRE_CORRENTES = 1

_CHAVES_PECA = frozenset({"tipo", "texto", "se", "fonte_se", "de", "corrente"})


class PecaInvalida(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de peças malformado ou com campos que não combinam com o tipo."""


class MateriaInvalida(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Matéria que a tela não deveria ter permitido montar (defeito, não erro do jogador)."""


class TipoPeca(StrEnum):
    FATO = "fato"
    OPINIAO = "opiniao"
    MANIPULACAO = "manipulacao"


class Nivel(IntEnum):
    PRECISA_MELHORAR = 0
    EM_PARTE = 1
    BEM_FEITO = 2


@dataclass(frozen=True)
class Peca:
    id: str
    tipo: TipoPeca
    texto: str
    se: frozenset[str] = frozenset()
    fonte_se: frozenset[str] = frozenset()
    de: str | None = None
    corrente: str | None = None

    def disponivel(self, estado: EstadoJogo) -> bool:
        return all(estado.tem_flag(flag) for flag in self.se)

    def pode_citar(self, estado: EstadoJogo) -> bool:
        """Fato: a fonte foi conferida; opinião: sempre; manipulação: nunca."""
        if self.tipo is TipoPeca.FATO:
            return all(estado.tem_flag(flag) for flag in self.fonte_se)
        return self.tipo is TipoPeca.OPINIAO


@dataclass(frozen=True)
class Inclusao:
    """Uma peça escolhida para a matéria, citando (fonte ou autoria) ou não."""

    peca: str
    citar: bool = False


@dataclass(frozen=True)
class Avaliacao:
    fatos: Nivel
    atribuicao: Nivel
    justica: Nivel

    @property
    def total(self) -> int:
        return int(self.fatos + self.atribuicao + self.justica)


class Pecas(Mapping[str, Peca]):
    """Catálogo imutável de peças da matéria, consultado pelo ID."""

    def __init__(self, pecas: dict[str, Peca] | None = None) -> None:
        self._pecas = dict(pecas or {})

    def __getitem__(self, id_peca: str) -> Peca:
        try:
            return self._pecas[id_peca]
        except KeyError:
            raise KeyError(f"peça inexistente: {id_peca!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._pecas)

    def __len__(self) -> int:
        return len(self._pecas)

    def ids_de_texto(self) -> set[str]:
        return {peca.texto for peca in self.values()}

    def flags_exigidas(self) -> set[str]:
        return set().union(*(peca.se | peca.fonte_se for peca in self.values()))

    def flags_marcadas(self) -> set[str]:
        return {FLAG_PUBLICOU}

    @classmethod
    def de_toml(cls, conteudo: str) -> Pecas:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise PecaInvalida(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Pecas:
        try:
            extras = set(dados) - {"pecas"}
            if extras:
                raise ValueError(f"chaves inesperadas no arquivo da matéria: {sorted(extras)}")
            tabela = dados.get("pecas", {})
            if not isinstance(tabela, dict):
                raise ValueError("'pecas' deveria ser uma tabela")
            pecas: dict[str, Peca] = {}
            _coletar(tabela, (), pecas)
        except ValueError as erro:
            raise PecaInvalida(str(erro)) from erro
        return cls(pecas)


def pecas_disponiveis(pecas: Pecas, estado: EstadoJogo) -> tuple[Peca, ...]:
    """As peças que o jogador já pode usar, na ordem do arquivo."""
    return tuple(peca for peca in pecas.values() if peca.disponivel(estado))


def avaliar(pecas: Pecas, estado: EstadoJogo, inclusoes: Iterable[Inclusao]) -> Avaliacao:
    """Avalia a matéria pelos três critérios do J7, lendo só flags de investigação."""
    escolhidas = _conferir(pecas, estado, list(inclusoes))

    fatos = [(peca, citar) for peca, citar in escolhidas if peca.tipo is TipoPeca.FATO]
    manipulacoes = [peca for peca, _ in escolhidas if peca.tipo is TipoPeca.MANIPULACAO]
    opinioes = [(peca, citar) for peca, citar in escolhidas if peca.tipo is TipoPeca.OPINIAO]

    return Avaliacao(
        fatos=_nivel(bons=sum(citar for _, citar in fatos), total=len(fatos) + len(manipulacoes)),
        atribuicao=_nivel(bons=sum(citar for _, citar in opinioes), total=len(opinioes)),
        justica=_justica(pecas, estado, [peca for peca, _ in opinioes]),
    )


def publicar(pecas: Pecas, estado: EstadoJogo, inclusoes: Iterable[Inclusao]) -> Avaliacao:
    """Avalia a versão final e marca `materia.publicou` (só uma ação, nunca uma nota: E1)."""
    avaliacao = avaliar(pecas, estado, inclusoes)
    estado.marcar_flag(FLAG_PUBLICOU)
    return avaliacao


def _nivel(bons: int, total: int) -> Nivel:
    """100% → bem feito; 50% ou mais → em parte; menos, ou nada incluído → precisa melhorar."""
    if total == 0:
        return Nivel.PRECISA_MELHORAR
    if bons == total:
        return Nivel.BEM_FEITO
    if 2 * bons >= total:
        return Nivel.EM_PARTE
    return Nivel.PRECISA_MELHORAR


def _justica(pecas: Pecas, estado: EstadoJogo, opinioes: list[Peca]) -> Nivel:
    """Só contagens: nenhuma corrente é tratada de forma diferente das outras (E2)."""
    ouvidas = {
        peca.corrente
        for peca in pecas_disponiveis(pecas, estado)
        if peca.tipo is TipoPeca.OPINIAO and peca.corrente is not None
    }
    presentes = Counter(peca.corrente for peca in opinioes if peca.corrente is not None)
    if len(presentes) < MINIMO_DE_CORRENTES:
        return Nivel.PRECISA_MELHORAR
    equilibradas = (
        max(presentes.values()) - min(presentes.values()) <= DIFERENCA_MAXIMA_ENTRE_CORRENTES
    )
    if set(presentes) == ouvidas and equilibradas:
        return Nivel.BEM_FEITO
    return Nivel.EM_PARTE


def _conferir(
    pecas: Pecas, estado: EstadoJogo, inclusoes: list[Inclusao]
) -> list[tuple[Peca, bool]]:
    vistas: set[str] = set()
    escolhidas = []
    for inclusao in inclusoes:
        if inclusao.peca not in pecas:
            raise MateriaInvalida(f"peça inexistente: {inclusao.peca!r}")
        if inclusao.peca in vistas:
            raise MateriaInvalida(f"peça repetida na matéria: {inclusao.peca!r}")
        vistas.add(inclusao.peca)
        peca = pecas[inclusao.peca]
        if not peca.disponivel(estado):
            raise MateriaInvalida(f"peça ainda indisponível: {peca.id!r}")
        if inclusao.citar and not peca.pode_citar(estado):
            raise MateriaInvalida(f"a peça {peca.id!r} não pode ser citada agora")
        escolhidas.append((peca, inclusao.citar))
    return escolhidas


# As funções abaixo levantam `ValueError`; `Pecas.de_dict` converte em `PecaInvalida`.


def _coletar(tabela: dict[str, object], caminho: tuple[str, ...], saida: dict[str, Peca]) -> None:
    for chave, valor in tabela.items():
        trecho = (*caminho, chave)
        nome = ".".join(trecho)
        if "." in chave:
            raise ValueError(f"ID inválido: {nome!r} (use tabelas aninhadas, não pontos)")
        validar_id(nome)
        if not isinstance(valor, dict):
            raise ValueError(f"valor solto em {nome!r}: uma peça é uma tabela com 'tipo'")
        if "tipo" in valor:
            saida[nome] = _peca(nome, valor)
        else:
            _coletar(valor, trecho, saida)


def _id(onde: str, valor: object) -> str:
    try:
        return validar_id(valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _flags(onde: str, valor: object) -> frozenset[str]:
    if not isinstance(valor, list):
        raise ValueError(f"{onde}: deveria ser uma lista de flags")
    return frozenset(_id(onde, flag) for flag in valor)


def _peca(id_peca: str, dados: dict[str, object]) -> Peca:
    onde = f"peça {id_peca!r}"
    extras = set(dados) - _CHAVES_PECA
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    if "texto" not in dados:
        raise ValueError(f"{onde}: falta a chave 'texto'")
    try:
        tipo = TipoPeca(dados["tipo"])
    except ValueError:
        aceitos = ", ".join(TipoPeca)
        raise ValueError(f"{onde}: tipo desconhecido {dados['tipo']!r} ({aceitos})") from None

    if "fonte_se" in dados and tipo is not TipoPeca.FATO:
        raise ValueError(f"{onde}: só um fato leva 'fonte_se'")
    for so_opiniao in ("de", "corrente"):
        if so_opiniao in dados and tipo is not TipoPeca.OPINIAO:
            raise ValueError(f"{onde}: só uma opinião leva {so_opiniao!r}")
    de = corrente = None
    if tipo is TipoPeca.OPINIAO:
        if "de" not in dados:
            raise ValueError(f"{onde}: uma opinião precisa de 'de' (quem disse)")
        de = _id(f"{onde}, de", dados["de"])
        if "corrente" in dados:
            try:
                corrente = validar_corrente(dados["corrente"])
            except ValueError as erro:
                raise ValueError(f"{onde}: {erro}") from None

    return Peca(
        id=id_peca,
        tipo=tipo,
        texto=_id(f"{onde}, texto", dados["texto"]),
        se=_flags(f"{onde}, se", dados.get("se", [])),
        fonte_se=_flags(f"{onde}, fonte_se", dados.get("fonte_se", [])),
        de=de,
        corrente=corrente,
    )
