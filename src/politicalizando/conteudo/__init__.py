"""Dados revisáveis do jogo (textos, roteiros, diálogos, cenas e fichas) e a leitura deles.

Fica fora de `dominio/` porque mexe em arquivos; as regras de cada formato estão no domínio.
Os arquivos são lidos por `importlib.resources`, que funciona no código-fonte, no pacote
instalado e no executável. O que tem texto fica na pasta do idioma; o que só tem IDs (como os
roteiros, os diálogos, as cenas e as fichas) fica na raiz de `conteudo/`.
"""

from importlib.resources import files

from politicalizando.dominio.cenas import Cenas, conferir_referencias
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.fichas import Fichas
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
    """Lê `conteudo/cenas.toml` e confere se os roteiros e diálogos citados existem.

    Levanta `CenaInvalida` se o arquivo não bate ou se uma referência está quebrada.
    """
    arquivo = files(__name__) / "cenas.toml"
    cenas = Cenas.de_toml(arquivo.read_text(encoding="utf-8"))
    conferir_referencias(cenas, carregar_roteiros(), carregar_dialogos())
    return cenas


def carregar_fichas() -> Fichas:
    """Lê `conteudo/fichas.toml`; levanta `FichaInvalida` se o arquivo não bate."""
    arquivo = files(__name__) / "fichas.toml"
    return Fichas.de_toml(arquivo.read_text(encoding="utf-8"))
