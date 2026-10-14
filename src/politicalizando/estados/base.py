"""Classe base das telas do jogo."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from politicalizando.jogo import Jogo


class Estado:
    """Uma tela do jogo. O `Jogo` repassa eventos e chama atualizar/desenhar a cada quadro."""

    def __init__(self, jogo: Jogo) -> None:
        self.jogo = jogo

    def tratar_evento(self, evento: pygame.Event) -> None:
        """Reage a um evento (tecla, mouse). Por padrão, ignora."""

    def atualizar(self, dt: float) -> None:
        """Avança a lógica da tela em `dt` segundos. Por padrão, não faz nada."""

    def desenhar(self, tela: pygame.Surface) -> None:
        """Desenha a tela inteira na superfície da resolução lógica."""
