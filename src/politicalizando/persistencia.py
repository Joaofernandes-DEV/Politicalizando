"""Save do progresso em JSON, 1 slot, com autosave (D10, J8).

Fica fora de `dominio/` porque mexe em arquivos; as regras do estado estão em
`dominio/estado_jogo.py`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from politicalizando.dominio.estado_jogo import EstadoJogo, SaveInvalido

# Troca a pasta de dados (usado pelos testes para não tocar no save real).
VARIAVEL_DADOS = "POLITICALIZANDO_DADOS"
NOME_SAVE = "save.json"


def pasta_dados() -> Path:
    """Pasta `dados/` ao lado do jogo: do `.exe` empacotado ou da raiz do projeto."""
    if pasta := os.environ.get(VARIAVEL_DADOS):
        return Path(pasta)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "dados"
    # src/politicalizando/persistencia.py → raiz do projeto.
    return Path(__file__).resolve().parents[2] / "dados"


def caminho_save() -> Path:
    return pasta_dados() / NOME_SAVE


def existe_save(caminho: Path | None = None) -> bool:
    return (caminho or caminho_save()).is_file()


def salvar(estado: EstadoJogo, caminho: Path | None = None) -> None:
    """Grava o save e marca o estado como salvo.

    Escreve num arquivo temporário e só então troca pelo definitivo: se o jogo cair no meio
    da gravação, o save anterior continua inteiro.
    """
    caminho = caminho or caminho_save()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")
    texto = json.dumps(estado.para_dict(), ensure_ascii=False, indent=2) + "\n"
    temporario.write_text(texto, encoding="utf-8")
    os.replace(temporario, caminho)
    estado.marcar_salvo()


def carregar(caminho: Path | None = None) -> EstadoJogo | None:
    """Lê o save; devolve `None` se não houver.

    Um save ilegível levanta `SaveInvalido` e o arquivo nunca é apagado: quem chama decide
    o que mostrar ao jogador.
    """
    caminho = caminho or caminho_save()
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        raise SaveInvalido(f"save ilegível: {erro}") from erro
    return EstadoJogo.de_dict(dados)


def autosalvar(estado: EstadoJogo, bloqueado: bool, caminho: Path | None = None) -> bool:
    """Salva ao entrar numa cena só se houve mudança e nada está bloqueado (D10).

    Devolve `True` se gravou.
    """
    if bloqueado or not estado.alterado:
        return False
    salvar(estado, caminho)
    return True
