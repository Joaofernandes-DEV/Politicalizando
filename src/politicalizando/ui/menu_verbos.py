"""Menu de verbos Olhar / Usar / Falar, aberto ao lado do objeto escolhido (I4, I9)."""

from __future__ import annotations

from collections.abc import Mapping

import pygame

from politicalizando.config import ALTURA_TELA, LARGURA_TELA, Paleta
from politicalizando.dominio.cenas import Area, Verbo
from politicalizando.dominio.textos import Texto
from politicalizando.ui import teclas
from politicalizando.ui.texto import renderizar

ESPACO = 2
RESPIRO = 4

# Resposta de `tratar_evento` quando o menu se fecha sem escolher um verbo.
FECHAR = "fechar"


class MenuVerbos:
    def __init__(self, fonte: pygame.font.Font, textos: Mapping[str, Texto]) -> None:
        self.fonte = fonte
        # Na ordem das teclas 1, 2 e 3.
        self._opcoes = (
            (Verbo.OLHAR, textos["verbo.olhar"].texto),
            (Verbo.USAR, textos["verbo.usar"].texto),
            (Verbo.FALAR, textos["verbo.falar"].texto),
        )
        self._largura = max(fonte.size(rotulo)[0] for _, rotulo in self._opcoes) + 2 * RESPIRO
        self._altura_botao = fonte.get_linesize() + 2
        self.botoes: list[pygame.Rect] = []
        self._selecionado = 0

    @property
    def aberto(self) -> bool:
        return bool(self.botoes)

    def abrir(self, area: Area) -> None:
        """Abre à direita do objeto, ou à esquerda se não couber, sempre dentro da tela."""
        altura = len(self._opcoes) * self._altura_botao
        x = area.x + area.largura + ESPACO
        if x + self._largura > LARGURA_TELA:
            x = area.x - self._largura - ESPACO
        x = min(max(x, 0), LARGURA_TELA - self._largura)
        y = min(max(area.y, 0), ALTURA_TELA - altura)
        self.botoes = [
            pygame.Rect(x, y + indice * self._altura_botao, self._largura, self._altura_botao)
            for indice in range(len(self._opcoes))
        ]
        self._selecionado = 0

    def fechar(self) -> None:
        self.botoes = []

    def _botao_em(self, posicao: tuple[int, int]) -> int | None:
        return next(
            (indice for indice, botao in enumerate(self.botoes) if botao.collidepoint(posicao)),
            None,
        )

    def tratar_evento(self, evento: pygame.Event) -> Verbo | str | None:
        """O verbo escolhido, `FECHAR` (Esc ou clique fora) ou `None`. Fecha ao responder."""
        if not self.aberto:
            return None
        resposta: Verbo | str | None = None
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                resposta = FECHAR
            elif evento.key in teclas.CONFIRMAR:
                resposta = self._opcoes[self._selecionado][0]
            elif evento.key in teclas.ANTERIOR:
                self._selecionado = (self._selecionado - 1) % len(self._opcoes)
            elif evento.key in teclas.PROXIMO:
                self._selecionado = (self._selecionado + 1) % len(self._opcoes)
            elif (indice := teclas.numero(evento.key)) is not None and indice < len(self._opcoes):
                resposta = self._opcoes[indice][0]
        elif evento.type == pygame.MOUSEMOTION:
            if (indice := self._botao_em(evento.pos)) is not None:
                self._selecionado = indice
        elif teclas.clique_esquerdo(evento):
            indice = self._botao_em(evento.pos)
            resposta = FECHAR if indice is None else self._opcoes[indice][0]
        if resposta is not None:
            self.fechar()
        return resposta

    def desenhar(self, tela: pygame.Surface) -> None:
        if not self.aberto:
            return
        for indice, ((_, rotulo), botao) in enumerate(zip(self._opcoes, self.botoes, strict=True)):
            cor = Paleta.DESTAQUE if indice == self._selecionado else Paleta.TEXTO
            pygame.draw.rect(tela, Paleta.FUNDO, botao)
            pygame.draw.rect(tela, cor, botao, 1)
            tela.blit(renderizar(self.fonte, rotulo, cor), (botao.x + RESPIRO, botao.y + 1))
