"""Ponto de entrada: `python -m politicalizando [--fechar-em SEGUNDOS]`."""

import argparse
from collections.abc import Sequence

import pygame

from politicalizando import __version__
from politicalizando.estados.titulo import EstadoTitulo
from politicalizando.jogo import Jogo


def analisar_argumentos(argumentos: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="politicalizando", description="Politicalizando")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--fechar-em",
        type=float,
        default=None,
        metavar="SEGUNDOS",
        help="fecha o jogo sozinho depois desse tempo (teste automático do executável)",
    )
    return parser.parse_args(argumentos)


def preparar_jogo(opcoes: argparse.Namespace) -> Jogo:
    jogo = Jogo()
    jogo.trocar_estado(EstadoTitulo(jogo))
    if opcoes.fechar_em is not None:
        # Um evento QUIT agendado: o jogo encerra pelo caminho normal, como se a janela fechasse.
        pygame.time.set_timer(pygame.Event(pygame.QUIT), round(opcoes.fechar_em * 1000), loops=1)
    return jogo


def main(argumentos: Sequence[str] | None = None) -> None:
    preparar_jogo(analisar_argumentos(argumentos)).executar()


if __name__ == "__main__":
    main()
