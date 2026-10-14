"""Dados revisáveis do jogo (textos, roteiros e, depois, cenas e diálogos) e a leitura deles.

Fica fora de `dominio/` porque mexe em arquivos; as regras de cada formato estão no domínio.
Os arquivos são lidos por `importlib.resources`, que funciona no código-fonte, no pacote
instalado e no executável. O que tem texto fica na pasta do idioma; o que só tem IDs (como os
roteiros) fica na raiz de `conteudo/`.
"""

from importlib.resources import files

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
