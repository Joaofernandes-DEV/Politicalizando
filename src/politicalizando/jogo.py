"""Loop principal e troca de estados (telas) do jogo."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from politicalizando.config import ALTURA_TELA, FPS, LARGURA_TELA, TITULO
from politicalizando.conteudo import carregar_interacao, carregar_mapa, carregar_textos

if TYPE_CHECKING:
    from politicalizando.estados.base import Estado


class Jogo:
    """Dono da janela e do único loop do jogo; a tela atual é o `estado`."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITULO)
        # SCALED amplia a resolução lógica para a janela sem borrar a pixel art.
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.SCALED)
        self.relogio = pygame.time.Clock()
        # Todo texto de tela vem daqui, pelo ID (`self.textos["titulo.frase"]`).
        self.textos = carregar_textos()
        # Cenas, roteiros, diálogos e casos, conferidos ao abrir: um dado quebrado falha cedo.
        self.interacao = carregar_interacao()
        self.mapa = carregar_mapa()
        self.estado: Estado | None = None
        self.rodando = False

    def trocar_estado(self, estado: Estado) -> None:
        self.estado = estado

    def encerrar(self) -> None:
        """Pede o fim do loop; o pygame é encerrado ao sair de `executar`."""
        self.rodando = False

    def executar(self) -> None:
        self.rodando = True
        try:
            while self.rodando:
                dt = self.relogio.tick(FPS) / 1000
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        self.encerrar()
                    elif self.estado is not None:
                        self.estado.tratar_evento(evento)
                if not self.rodando:
                    break
                if self.estado is not None:
                    self.estado.atualizar(dt)
                    self.estado.desenhar(self.tela)
                pygame.display.flip()
        finally:
            pygame.quit()
