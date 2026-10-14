"""Tela de título provisória da Fase 0: mostra o nome do jogo e fecha com Esc."""

import pygame

from politicalizando import __version__
from politicalizando.config import LARGURA_TELA, TITULO, Paleta
from politicalizando.estados.base import Estado
from politicalizando.jogo import Jogo


class EstadoTitulo(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        # Fonte padrão do pygame até a fonte pixel com acentos chegar (Fase 3, I2).
        fonte_titulo = pygame.font.Font(None, 28)
        fonte_texto = pygame.font.Font(None, 16)
        # Sem antialiasing: o texto fica com o mesmo pixel duro da arte.
        self._linhas = [
            (fonte_titulo.render(TITULO.upper(), False, Paleta.DESTAQUE), 62),
            (fonte_texto.render("Pensar antes de escolher um lado.", False, Paleta.TEXTO), 92),
            (fonte_texto.render("Esc: sair", False, Paleta.APAGADO), 150),
            (fonte_texto.render(f"v{__version__}", False, Paleta.APAGADO), 164),
        ]

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.jogo.encerrar()

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        for superficie, y in self._linhas:
            tela.blit(superficie, superficie.get_rect(midtop=(LARGURA_TELA // 2, y)))
