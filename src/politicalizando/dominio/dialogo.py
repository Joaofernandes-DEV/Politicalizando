"""Árvores de diálogo em dados, executadas pelo diretor como um roteiro comum (J2, D11).

Cada tabela com `inicio` é um diálogo, e o caminho dela é o ID. Os nós ficam em `nos`; cada nó
tem `passos` no formato dos roteiros e, depois deles, oferece `opcoes`, segue sozinho para outro
nó (`vai_para`) ou termina:

    [exemplo.guia]
    inicio = "ola"

    [exemplo.guia.nos.ola]
    passos = [{ fala = "exemplo.guia.ola" }]

    [[exemplo.guia.nos.ola.opcoes]]
    id = "posicao"
    texto = "exemplo.guia.pergunta_posicao"
    vai_para = "posicao"
    uso_unico = true

    [exemplo.guia.nos.posicao]
    passos = [{ fala = "exemplo.guia.resposta_posicao" }]
    vai_para = "ola"

Escolher uma opção marca a flag `<id do diálogo>.<id da opção>` (ex.: `exemplo.guia.posicao`,
"perguntou a posição"). Ela esconde as opções de uso único e alimenta as condições `se` (flags
que precisam estar marcadas) e `se_nao` (flags que não podem estar). Como as flags vão no save,
uma opção usada continua escondida nas conversas seguintes. As flags registram só a
investigação, nunca um alinhamento (E1). `corrente` marca o diálogo para o teste de
equilíbrio E3.
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from politicalizando.dominio.acoes import Acao, Escolha, Fala, MarcarFlag, Roteiro
from politicalizando.dominio.correntes import validar_corrente
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id
from politicalizando.dominio.roteiro import ler_passos

# Destino especial: encerra o diálogo. Não pode ser o nome de um nó.
FIM = "fim"

_CHAVES_DIALOGO = frozenset({"inicio", "corrente", "nos"})
_CHAVES_NO = frozenset({"passos", "opcoes", "vai_para"})
_CHAVES_OPCAO = frozenset({"id", "texto", "vai_para", "uso_unico", "se", "se_nao"})


class DialogoInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de diálogos malformado: sintaxe, ID, nó, opção ou ligação fora do formato."""


@dataclass(frozen=True)
class Opcao:
    id: str
    texto: str
    vai_para: str
    flag: str
    uso_unico: bool = False
    se: frozenset[str] = frozenset()
    se_nao: frozenset[str] = frozenset()

    def visivel(self, estado: EstadoJogo) -> bool:
        if self.uso_unico and estado.tem_flag(self.flag):
            return False
        return all(estado.tem_flag(flag) for flag in self.se) and not any(
            estado.tem_flag(flag) for flag in self.se_nao
        )


@dataclass(frozen=True)
class No:
    id: str
    passos: tuple[Acao, ...] = ()
    opcoes: tuple[Opcao, ...] = ()
    vai_para: str | None = None


@dataclass(frozen=True)
class Dialogo:
    id: str
    inicio: str
    nos: Mapping[str, No] = field(default_factory=dict)
    corrente: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "nos", MappingProxyType(dict(self.nos)))

    def executar(self, estado: EstadoJogo) -> Roteiro:
        """Um gerador novo a cada chamada, pronto para o `Diretor`."""
        no = self.nos[self.inicio]
        while True:
            yield from no.passos
            if no.vai_para is not None:
                destino = no.vai_para
            else:
                visiveis = [opcao for opcao in no.opcoes if opcao.visivel(estado)]
                if not visiveis:
                    return
                # ids-de-texto: dados (conferidos a partir do dialogos.toml)
                indice = yield Escolha(tuple(opcao.texto for opcao in visiveis))
                escolhida = visiveis[indice]
                yield MarcarFlag(escolhida.flag)
                destino = escolhida.vai_para
            if destino == FIM:
                return
            no = self.nos[destino]

    def _opcoes(self) -> Iterator[Opcao]:
        for no in self.nos.values():
            yield from no.opcoes

    def ids_de_texto(self) -> set[str]:
        """IDs das falas dos nós e dos textos das opções."""
        falas = {
            acao.id_texto
            for no in self.nos.values()
            for acao in no.passos
            if isinstance(acao, Fala)
        }
        return falas | {opcao.texto for opcao in self._opcoes()}

    def flags_exigidas(self) -> set[str]:
        """Flags citadas nas condições `se` e `se_nao` das opções."""
        return set().union(*(opcao.se | opcao.se_nao for opcao in self._opcoes()))

    def flags_marcadas(self) -> set[str]:
        """Flags que o diálogo pode marcar: as das opções e as dos passos."""
        dos_passos = {
            acao.flag
            for no in self.nos.values()
            for acao in no.passos
            if isinstance(acao, MarcarFlag)
        }
        return dos_passos | {opcao.flag for opcao in self._opcoes()}


class Dialogos(Mapping[str, Dialogo]):
    """Catálogo imutável de diálogos, consultado pelo ID."""

    def __init__(self, dialogos: dict[str, Dialogo] | None = None) -> None:
        self._dialogos = dict(dialogos or {})

    def __getitem__(self, id_dialogo: str) -> Dialogo:
        try:
            return self._dialogos[id_dialogo]
        except KeyError:
            raise KeyError(f"diálogo inexistente: {id_dialogo!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._dialogos)

    def __len__(self) -> int:
        return len(self._dialogos)

    def ids_de_texto(self) -> set[str]:
        return set().union(*(dialogo.ids_de_texto() for dialogo in self.values()))

    def flags_exigidas(self) -> set[str]:
        return set().union(*(dialogo.flags_exigidas() for dialogo in self.values()))

    def flags_marcadas(self) -> set[str]:
        return set().union(*(dialogo.flags_marcadas() for dialogo in self.values()))

    @classmethod
    def de_toml(cls, conteudo: str) -> Dialogos:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise DialogoInvalido(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Dialogos:
        """Achata as tabelas aninhadas em IDs com ponto e valida cada diálogo."""
        dialogos: dict[str, Dialogo] = {}
        try:
            _coletar(dados, (), dialogos)
        except DialogoInvalido:
            raise
        except ValueError as erro:
            raise DialogoInvalido(str(erro)) from erro
        return cls(dialogos)


# As funções abaixo levantam `ValueError`; `Dialogos.de_dict` converte em `DialogoInvalido`.


def _coletar(
    tabela: dict[str, object], caminho: tuple[str, ...], saida: dict[str, Dialogo]
) -> None:
    for chave, valor in tabela.items():
        trecho = (*caminho, chave)
        nome = ".".join(trecho)
        if "." in chave:
            raise ValueError(f"ID inválido: {nome!r} (use tabelas aninhadas, não pontos)")
        validar_id(nome)
        if not isinstance(valor, dict):
            raise ValueError(f"valor solto em {nome!r}: um diálogo é uma tabela com 'inicio'")
        if "inicio" in valor:
            saida[nome] = _dialogo(nome, valor)
        else:
            _coletar(valor, trecho, saida)


def _chaves(onde: str, tabela: dict[str, object], aceitas: frozenset[str]) -> None:
    extras = set(tabela) - aceitas
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")


def _trecho(onde: str, valor: object) -> str:
    """Valida um nome de um trecho só (nó, opção): sem pontos."""
    if not isinstance(valor, str) or "." in valor:
        raise ValueError(f"{onde}: nome inválido {valor!r}")
    try:
        return validar_id(valor)
    except ValueError:
        raise ValueError(f"{onde}: nome inválido {valor!r}") from None


def _flags(onde: str, valor: object) -> frozenset[str]:
    if not isinstance(valor, list):
        raise ValueError(f"{onde}: deveria ser uma lista de flags")
    try:
        return frozenset(validar_id(flag) for flag in valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _dialogo(id_dialogo: str, dados: dict[str, object]) -> Dialogo:
    onde = repr(id_dialogo)
    _chaves(onde, dados, _CHAVES_DIALOGO)
    inicio = _trecho(f"{onde}, inicio", dados["inicio"])
    corrente = dados.get("corrente")
    if corrente is not None:
        try:
            validar_corrente(corrente)
        except ValueError as erro:
            raise ValueError(f"{onde}: {erro}") from None
    tabela_nos = dados.get("nos")
    if not isinstance(tabela_nos, dict) or not tabela_nos:
        raise ValueError(f"{onde}: o diálogo precisa de uma tabela 'nos' com pelo menos um nó")

    nos = {
        _trecho(f"{onde}, nó", nome): _no(id_dialogo, nome, valor)
        for nome, valor in tabela_nos.items()
    }
    if FIM in nos:
        raise ValueError(f"{onde}: {FIM!r} é reservado e não pode ser o nome de um nó")
    dialogo = Dialogo(id=id_dialogo, inicio=inicio, nos=nos, corrente=corrente)
    _conferir_ligacoes(dialogo)
    return dialogo


def _no(id_dialogo: str, nome: str, dados: object) -> No:
    onde = f"{id_dialogo!r}, nó {nome!r}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: um nó é uma tabela")
    _chaves(onde, dados, _CHAVES_NO)
    if not dados:
        raise ValueError(f"{onde}: nó vazio")
    if "opcoes" in dados and "vai_para" in dados:
        raise ValueError(f"{onde}: use 'opcoes' ou 'vai_para', não os dois")

    passos = ler_passos(dados.get("passos", []), onde)
    vai_para = None
    if "vai_para" in dados:
        vai_para = _trecho(f"{onde}, vai_para", dados["vai_para"])

    opcoes: tuple[Opcao, ...] = ()
    if "opcoes" in dados:
        lista = dados["opcoes"]
        if not isinstance(lista, list) or not lista:
            raise ValueError(f"{onde}: 'opcoes' deveria ser uma lista com pelo menos uma opção")
        opcoes = tuple(_opcao(id_dialogo, onde, numero, op) for numero, op in enumerate(lista, 1))
        textos = [opcao.texto for opcao in opcoes]
        if len(set(textos)) != len(textos):
            raise ValueError(f"{onde}: duas opções com o mesmo texto")
    elif not passos and vai_para is None:
        raise ValueError(f"{onde}: nó vazio")
    return No(id=nome, passos=passos, opcoes=opcoes, vai_para=vai_para)


def _opcao(id_dialogo: str, onde_no: str, numero: int, dados: object) -> Opcao:
    onde = f"{onde_no}, opção {numero}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: uma opção é uma tabela")
    _chaves(onde, dados, _CHAVES_OPCAO)
    for obrigatoria in ("id", "texto", "vai_para"):
        if obrigatoria not in dados:
            raise ValueError(f"{onde}: falta a chave {obrigatoria!r}")
    id_opcao = _trecho(f"{onde}, id", dados["id"])
    try:
        texto = validar_id(dados["texto"])
    except ValueError as erro:
        raise ValueError(f"{onde}: texto {erro}") from None
    uso_unico = dados.get("uso_unico", False)
    if not isinstance(uso_unico, bool):
        raise ValueError(f"{onde}: 'uso_unico' deveria ser true ou false")
    return Opcao(
        id=id_opcao,
        texto=texto,
        vai_para=_trecho(f"{onde}, vai_para", dados["vai_para"]),
        flag=f"{id_dialogo}.{id_opcao}",
        uso_unico=uso_unico,
        se=_flags(f"{onde}, se", dados.get("se", [])),
        se_nao=_flags(f"{onde}, se_nao", dados.get("se_nao", [])),
    )


def _conferir_ligacoes(dialogo: Dialogo) -> None:
    """Destinos existentes, ids de opção únicos, todo nó alcançável e nenhum laço sem escolha."""
    onde = repr(dialogo.id)
    if dialogo.inicio not in dialogo.nos:
        raise ValueError(f"{onde}: o nó de início {dialogo.inicio!r} não existe")

    ids_opcoes = [opcao.id for opcao in dialogo._opcoes()]
    repetidos = sorted({id_opcao for id_opcao in ids_opcoes if ids_opcoes.count(id_opcao) > 1})
    if repetidos:
        raise ValueError(f"{onde}: ids de opção repetidos no diálogo: {repetidos}")

    def destinos(no: No) -> list[str]:
        alvos = [no.vai_para] if no.vai_para is not None else []
        return alvos + [opcao.vai_para for opcao in no.opcoes]

    for no in dialogo.nos.values():
        for destino in destinos(no):
            if destino != FIM and destino not in dialogo.nos:
                raise ValueError(f"{onde}, nó {no.id!r}: destino {destino!r} não existe")

    alcancados = {dialogo.inicio}
    pendentes = [dialogo.inicio]
    while pendentes:
        for destino in destinos(dialogo.nos[pendentes.pop()]):
            if destino != FIM and destino not in alcancados:
                alcancados.add(destino)
                pendentes.append(destino)
    orfaos = sorted(set(dialogo.nos) - alcancados)
    if orfaos:
        raise ValueError(f"{onde}: nós que nunca são alcançados a partir do início: {orfaos}")

    # Um laço só de `vai_para` rodaria para sempre sem o jogador escolher nada.
    for nome in dialogo.nos:
        vistos = []
        atual: str | None = nome
        while atual is not None and atual != FIM:
            if atual in vistos:
                raise ValueError(f"{onde}: laço sem escolha entre os nós {vistos}")
            vistos.append(atual)
            atual = dialogo.nos[atual].vai_para
