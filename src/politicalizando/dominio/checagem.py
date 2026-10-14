"""Checagem de fontes: posts, manchetes e falas classificados pelo jogador (J4, C6, R9, E5).

Formato de `conteudo/checagem.toml` (os textos ficam no `textos.toml`, por ID):

    [casos.praca.cartaz]
    tipo = "manchete"
    conteudo = "caso.praca.cartaz.texto"
    classe = "fato"
    confere = false
    explicacao = "caso.praca.cartaz.explicacao"
    fontes = [{ autor = "Autor", titulo = "Título", ano = 2026, editora = "Editora" }]

Cada tabela de `casos` com `classe` é um caso, e o caminho dela é o ID. As classes são:

- `fato`: fato verificável. Tem `confere` (o que a fonte mostra) e fontes obrigatórias: um fato
  não é relativizado como "mais uma opinião" (C6).
- `opiniao`: opinião ou valor; não tem resposta certa, então não leva `confere` nem `origem`.
- `manipulacao`: leva `origem` (uma das 4 correntes ou "sem_lado", para golpes e caça-cliques) e
  a `tecnica` usada. A origem existe só para o teste de equilíbrio E5: os exemplos se
  distribuem por igual entre as correntes.

O jogador vê o conteúdo, escolhe a classe e sempre recebe a explicação; errar nunca pune (J11).
Classificar marca `<caso>.checou` e, se acertou, `<caso>.acertou`: só investigação (E1).
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from enum import StrEnum

from politicalizando.dominio.acoes import Escolha, Fala, MarcarFlag, Roteiro
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id
from politicalizando.dominio.fontes import Fonte, ler_fonte

# Origem de um exemplo de manipulação que não vem de nenhuma corrente (golpes, caça-cliques).
SEM_LADO = "sem_lado"


class Classe(StrEnum):
    FATO = "fato"
    OPINIAO = "opiniao"
    MANIPULACAO = "manipulacao"


class TipoCaso(StrEnum):
    POST = "post"
    MANCHETE = "manchete"
    FALA = "fala"


class Tecnica(StrEnum):
    FORA_DE_CONTEXTO = "fora_de_contexto"
    DADO_FALSO = "dado_falso"
    MANCHETE_ENGANOSA = "manchete_enganosa"
    APELO_A_EMOCAO = "apelo_a_emocao"
    FALSA_AUTORIDADE = "falsa_autoridade"
    CACA_CLIQUE = "caca_clique"
    GOLPE = "golpe"


# Ordem fixa das opções na tela; os rótulos ficam no textos.toml.
ORDEM_DAS_CLASSES = (Classe.FATO, Classe.OPINIAO, Classe.MANIPULACAO)

_CHAVES_CASO = frozenset(
    {"tipo", "conteudo", "classe", "explicacao", "confere", "origem", "tecnica", "fontes"}
)
_PROIBIDAS = {
    Classe.FATO: {"origem", "tecnica"},
    Classe.OPINIAO: {"confere", "origem", "tecnica"},
    Classe.MANIPULACAO: {"confere"},
}


class CasoInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de checagem malformado ou com campos que não combinam com a classe."""


@dataclass(frozen=True)
class Caso:
    id: str
    tipo: TipoCaso
    conteudo: str
    classe: Classe
    explicacao: str
    confere: bool | None = None
    origem: str | None = None
    tecnica: Tecnica | None = None
    fontes: tuple[Fonte, ...] = ()

    @property
    def flag_checou(self) -> str:
        return f"{self.id}.checou"

    @property
    def flag_acertou(self) -> str:
        return f"{self.id}.acertou"

    def executar(self, estado: EstadoJogo) -> Roteiro:
        """Um gerador novo a cada chamada, pronto para o `Diretor`."""
        # ids-de-texto: dados (conteúdo e explicação vêm do checagem.toml)
        yield Fala(self.conteudo)
        indice = yield Escolha(
            ("checagem.classe.fato", "checagem.classe.opiniao", "checagem.classe.manipulacao")
        )
        yield MarcarFlag(self.flag_checou)
        if ORDEM_DAS_CLASSES[indice] == self.classe:
            yield MarcarFlag(self.flag_acertou)
            yield Fala("checagem.resultado.certo")
        else:
            yield Fala("checagem.resultado.errado")
        # ids-de-texto: dados
        yield Fala(self.explicacao)


class Casos(Mapping[str, Caso]):
    """Catálogo imutável de casos de checagem, consultado pelo ID."""

    def __init__(self, casos: dict[str, Caso] | None = None) -> None:
        self._casos = dict(casos or {})

    def __getitem__(self, id_caso: str) -> Caso:
        try:
            return self._casos[id_caso]
        except KeyError:
            raise KeyError(f"caso inexistente: {id_caso!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._casos)

    def __len__(self) -> int:
        return len(self._casos)

    def ids_de_texto(self) -> set[str]:
        return {id_texto for caso in self.values() for id_texto in (caso.conteudo, caso.explicacao)}

    def flags_marcadas(self) -> set[str]:
        return {flag for caso in self.values() for flag in (caso.flag_checou, caso.flag_acertou)}

    @classmethod
    def de_toml(cls, conteudo: str) -> Casos:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise CasoInvalido(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Casos:
        try:
            extras = set(dados) - {"casos"}
            if extras:
                raise ValueError(f"chaves inesperadas no arquivo de checagem: {sorted(extras)}")
            tabela = dados.get("casos", {})
            if not isinstance(tabela, dict):
                raise ValueError("'casos' deveria ser uma tabela")
            casos: dict[str, Caso] = {}
            _coletar(tabela, (), casos)
        except ValueError as erro:
            raise CasoInvalido(str(erro)) from erro
        return cls(casos)


# As funções abaixo levantam `ValueError`; `Casos.de_dict` converte em `CasoInvalido`.


def _coletar(tabela: dict[str, object], caminho: tuple[str, ...], saida: dict[str, Caso]) -> None:
    for chave, valor in tabela.items():
        trecho = (*caminho, chave)
        nome = ".".join(trecho)
        if "." in chave:
            raise ValueError(f"ID inválido: {nome!r} (use tabelas aninhadas, não pontos)")
        validar_id(nome)
        if not isinstance(valor, dict):
            raise ValueError(f"valor solto em {nome!r}: um caso é uma tabela com 'classe'")
        if "classe" in valor:
            saida[nome] = _caso(nome, valor)
        else:
            _coletar(valor, trecho, saida)


def _enum(onde: str, tipo: type[StrEnum], valor: object) -> StrEnum:
    try:
        return tipo(valor)
    except ValueError:
        aceitos = ", ".join(tipo)
        raise ValueError(f"{onde}: valor desconhecido {valor!r} (aceitos: {aceitos})") from None


def _id(onde: str, valor: object) -> str:
    try:
        return validar_id(valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _caso(id_caso: str, dados: dict[str, object]) -> Caso:
    onde = f"caso {id_caso!r}"
    extras = set(dados) - _CHAVES_CASO
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    for obrigatoria in ("tipo", "conteudo", "classe", "explicacao"):
        if obrigatoria not in dados:
            raise ValueError(f"{onde}: falta a chave {obrigatoria!r}")

    classe = _enum(f"{onde}, classe", Classe, dados["classe"])
    proibidas = sorted(_PROIBIDAS[classe] & set(dados))
    if proibidas:
        raise ValueError(f"{onde}: um caso de {classe} não leva {proibidas}")

    fontes_brutas = dados.get("fontes", [])
    if not isinstance(fontes_brutas, list):
        raise ValueError(f"{onde}: 'fontes' deveria ser uma lista")
    fontes = tuple(
        ler_fonte(fonte, f"{onde}, fonte {numero}") for numero, fonte in enumerate(fontes_brutas, 1)
    )

    confere = origem = tecnica = None
    if classe is Classe.FATO:
        confere = dados.get("confere")
        if not isinstance(confere, bool):
            raise ValueError(f"{onde}: um fato precisa de 'confere' (true ou false)")
        if not fontes:
            raise ValueError(f"{onde}: um fato precisa de pelo menos uma fonte")
    elif classe is Classe.MANIPULACAO:
        for obrigatoria in ("origem", "tecnica"):
            if obrigatoria not in dados:
                raise ValueError(f"{onde}: uma manipulação precisa de {obrigatoria!r}")
        origem = dados["origem"]
        if origem != SEM_LADO and origem not in CORRENTES:
            raise ValueError(
                f"{onde}: origem desconhecida {origem!r} (use uma corrente ou {SEM_LADO!r})"
            )
        tecnica = _enum(f"{onde}, tecnica", Tecnica, dados["tecnica"])

    return Caso(
        id=id_caso,
        tipo=_enum(f"{onde}, tipo", TipoCaso, dados["tipo"]),
        conteudo=_id(f"{onde}, conteudo", dados["conteudo"]),
        classe=classe,
        explicacao=_id(f"{onde}, explicacao", dados["explicacao"]),
        confere=confere,
        origem=origem,
        tecnica=tecnica,
        fontes=fontes,
    )
