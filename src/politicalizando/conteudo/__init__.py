"""Dados revisáveis do jogo (textos, roteiros, diálogos, cenas, mapa, fichas, checagem e matéria).

Fica fora de `dominio/` porque mexe em arquivos; as regras de cada formato estão no domínio.
Os arquivos são lidos por `importlib.resources`, que funciona no código-fonte, no pacote
instalado e no executável. O que tem texto fica na pasta do idioma; o que só tem IDs (como os
roteiros, os diálogos, as cenas, o mapa, o caderno, as fichas, os casos de checagem e as peças
da matéria) fica na raiz de `conteudo/`.
"""

from importlib.resources import files

from politicalizando.dominio.caderno import Caderno
from politicalizando.dominio.cenas import Cenas, conferir_referencias
from politicalizando.dominio.checagem import Casos
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.fichas import Fichas
from politicalizando.dominio.interacao import Interacao
from politicalizando.dominio.mapa import Mapa, conferir_cenas
from politicalizando.dominio.materia import Pecas
from politicalizando.dominio.roteiro import Roteiros
from politicalizando.dominio.textos import Textos

IDIOMA_PADRAO = "pt_BR"


def carregar_textos(idioma: str = IDIOMA_PADRAO) -> Textos:
    """Lê `conteudo/<idioma>/textos.toml`; levanta `TextoInvalido` se o arquivo não bate."""
    arquivo = files(__name__) / idioma / "textos.toml"
    return Textos.de_toml(arquivo.read_text(encoding="utf-8"))


def carregar_roteiros() -> Roteiros:
    """Lê `conteudo/roteiros.toml`; levanta `RoteiroInvalido` se o arquivo não bate."""
    arquivo = files(__name__) / "roteiros.toml"
    return Roteiros.de_toml(arquivo.read_text(encoding="utf-8"))


def carregar_dialogos() -> Dialogos:
    """Lê `conteudo/dialogos.toml`; levanta `DialogoInvalido` se o arquivo não bate."""
    arquivo = files(__name__) / "dialogos.toml"
    return Dialogos.de_toml(arquivo.read_text(encoding="utf-8"))


def carregar_cenas() -> Cenas:
    """Lê `conteudo/cenas.toml` e confere se os roteiros, diálogos e casos citados existem.

    Levanta `CenaInvalida` se o arquivo não bate ou se uma referência está quebrada.
    """
    arquivo = files(__name__) / "cenas.toml"
    cenas = Cenas.de_toml(arquivo.read_text(encoding="utf-8"))
    conferir_referencias(cenas, carregar_roteiros(), carregar_dialogos(), carregar_checagem())
    return cenas


def carregar_interacao() -> Interacao:
    """As cenas com os roteiros, diálogos e casos que elas citam, prontos para a partida."""
    return Interacao(
        carregar_cenas(), carregar_roteiros(), carregar_dialogos(), carregar_checagem()
    )


def carregar_mapa() -> Mapa:
    """Lê `conteudo/mapa.toml` e confere se as cenas de destino existem.

    Levanta `MapaInvalido` se o arquivo não bate ou se um local leva a uma cena inexistente.
    """
    arquivo = files(__name__) / "mapa.toml"
    mapa = Mapa.de_toml(arquivo.read_text(encoding="utf-8"))
    conferir_cenas(mapa, carregar_cenas())
    return mapa


def carregar_caderno() -> Caderno:
    """Lê `conteudo/caderno.toml`; levanta `CadernoInvalido` se o arquivo não bate."""
    arquivo = files(__name__) / "caderno.toml"
    return Caderno.de_toml(arquivo.read_text(encoding="utf-8"))


def carregar_fichas() -> Fichas:
    """Lê `conteudo/fichas.toml`; levanta `FichaInvalida` se o arquivo não bate."""
    arquivo = files(__name__) / "fichas.toml"
    return Fichas.de_toml(arquivo.read_text(encoding="utf-8"))


def carregar_checagem() -> Casos:
    """Lê `conteudo/checagem.toml`; levanta `CasoInvalido` se o arquivo não bate."""
    arquivo = files(__name__) / "checagem.toml"
    return Casos.de_toml(arquivo.read_text(encoding="utf-8"))


def carregar_materia() -> Pecas:
    """Lê `conteudo/materia.toml`; levanta `PecaInvalida` se o arquivo não bate."""
    arquivo = files(__name__) / "materia.toml"
    return Pecas.de_toml(arquivo.read_text(encoding="utf-8"))
