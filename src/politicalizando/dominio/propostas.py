"""Comparação de propostas: como cada corrente propõe resolver o problema do capítulo (J5).

Formato de `conteudo/propostas.toml` (os textos ficam no `textos.toml`, por ID):

    [propostas.liberalismo]
    se = ["biblioteca.morador.posicao"]
    proposta = "proposta.liberalismo"
    pros = ["proposta.liberalismo.pro.1"]
    contras = ["proposta.liberalismo.contra.1"]
    valores = ["proposta.liberalismo.valor.1"]

A chave é a corrente, então há no máximo uma proposta por corrente. Todas têm o mesmo modelo
(proposta, prós, contras e valores em jogo) e saem sempre na ordem fixa das correntes, sem
resposta certa (C2). A proposta aparece quando as flags de `se` estão marcadas, por exemplo
depois de ouvir a posição do morador daquela corrente. O texto da proposta pode ser o mesmo do
item 5 da ficha. Ver a comparação com pelo menos duas propostas marca `comparacao.comparou`, só
uma ação de investigação (E1).
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from politicalizando.dominio.correntes import CORRENTES, validar_corrente
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id

FLAG_COMPAROU = "comparacao.comparou"
MINIMO_PARA_COMPARAR = 2

_LISTAS = ("pros", "contras", "valores")
_CHAVES = frozenset({"se", "proposta", *_LISTAS})


class PropostaInvalida(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de propostas malformado ou fora do modelo comum."""


@dataclass(frozen=True)
class Proposta:
    corrente: str
    proposta: str
    pros: tuple[str, ...]
    contras: tuple[str, ...]
    valores: tuple[str, ...]
    se: frozenset[str] = frozenset()

    def liberada(self, estado: EstadoJogo) -> bool:
        return all(estado.tem_flag(flag) for flag in self.se)

    def ids_de_texto(self) -> tuple[str, ...]:
        """Os textos da proposta, na ordem do modelo."""
        return (self.proposta, *self.pros, *self.contras, *self.valores)


class Propostas(Mapping[str, Proposta]):
    """Catálogo das propostas, sempre na ordem fixa de `CORRENTES`."""

    def __init__(self, propostas: dict[str, Proposta] | None = None) -> None:
        propostas = propostas or {}
        self._propostas = {c: propostas[c] for c in CORRENTES if c in propostas}

    def __getitem__(self, corrente: str) -> Proposta:
        try:
            return self._propostas[corrente]
        except KeyError:
            raise KeyError(f"proposta inexistente: {corrente!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._propostas)

    def __len__(self) -> int:
        return len(self._propostas)

    def liberadas(self, estado: EstadoJogo) -> tuple[Proposta, ...]:
        return tuple(proposta for proposta in self.values() if proposta.liberada(estado))

    def registrar_comparacao(self, estado: EstadoJogo) -> bool:
        """Marca `comparacao.comparou` se há pelo menos duas propostas para comparar."""
        if len(self.liberadas(estado)) < MINIMO_PARA_COMPARAR:
            return False
        return estado.marcar_flag(FLAG_COMPAROU)

    def ids_de_texto(self) -> set[str]:
        return {id_texto for proposta in self.values() for id_texto in proposta.ids_de_texto()}

    def flags_exigidas(self) -> set[str]:
        return set().union(*(proposta.se for proposta in self.values()))

    def flags_marcadas(self) -> set[str]:
        return {FLAG_COMPAROU}

    @classmethod
    def de_toml(cls, conteudo: str) -> Propostas:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise PropostaInvalida(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Propostas:
        try:
            extras = set(dados) - {"propostas"}
            if extras:
                raise ValueError(f"chaves inesperadas no arquivo de propostas: {sorted(extras)}")
            tabela = dados.get("propostas", {})
            if not isinstance(tabela, dict):
                raise ValueError("'propostas' deveria ser uma tabela")
            propostas = {}
            for corrente, valor in tabela.items():
                validar_corrente(corrente)
                propostas[corrente] = _proposta(corrente, valor)
        except ValueError as erro:
            raise PropostaInvalida(str(erro)) from erro
        return cls(propostas)


def _id(onde: str, valor: object) -> str:
    try:
        return validar_id(valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _proposta(corrente: str, dados: object) -> Proposta:
    onde = f"proposta {corrente!r}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: uma proposta é uma tabela")
    extras = set(dados) - _CHAVES
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    faltando = sorted(_CHAVES - {"se"} - set(dados))
    if faltando:
        raise ValueError(f"{onde}: faltam itens do modelo {faltando}")
    listas = {}
    for nome in _LISTAS:
        valor = dados[nome]
        if not isinstance(valor, list) or not valor:
            raise ValueError(f"{onde}, {nome}: deveria ser uma lista com pelo menos um item")
        listas[nome] = tuple(_id(f"{onde}, {nome}", item) for item in valor)
    se = dados.get("se", [])
    if not isinstance(se, list):
        raise ValueError(f"{onde}, se: deveria ser uma lista de flags")
    return Proposta(
        corrente=corrente,
        proposta=_id(f"{onde}, proposta", dados["proposta"]),
        se=frozenset(_id(f"{onde}, se", flag) for flag in se),
        **listas,
    )
