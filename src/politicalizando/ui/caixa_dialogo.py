"""Caixa de diálogo: mostra a fala ou a escolha que o diretor espera (I3, I4).

Nesta fase o texto aparece inteiro de uma vez (o texto aos poucos é da Fase 3). Uma fala avança
com clique, Enter ou Espaço; uma escolha responde ao mouse, às setas com Enter e aos números.
"""

from __future__ import annotations

from collections.abc import Mapping

import pygame

from politicalizando.config import ALTURA_TELA, LARGURA_TELA, Paleta
from politicalizando.dominio.acoes import AcaoDeEspera, Escolha, Fala
from politicalizando.dominio.textos import Texto
from politicalizando.ui import teclas
from politicalizando.ui.texto import quebrar_linhas, renderizar

MARGEM = 4
RESPIRO = 4
MINIMO_DE_LINHAS = 2
# Todo texto do jogo precisa caber nesse limite (tests/test_ui.py).
MAXIMO_DE_LINHAS = 4

# Resposta de `tratar_evento` para uma fala; numa escolha, a resposta é o índice da opção.
CONFIRMAR = "confirmar"


class CaixaDialogo:
    def __init__(self, fonte: pygame.font.Font, textos: Mapping[str, Texto]) -> None:
        self.fonte = fonte
        self.textos = textos
        self.altura_linha = fonte.get_linesize()
        self.largura_texto = LARGURA_TELA - 2 * (MARGEM + RESPIRO)
        self._acao: AcaoDeEspera | None = None
        self._linhas: list[str] = []
        self._selecionada = 0
        self.retangulo = pygame.Rect(0, 0, 0, 0)

    def linhas_da_fala(self, id_texto: str) -> list[str]:
        # ids-de-texto: dados (a fala vem dos roteiros, diálogos e cenas)
        return quebrar_linhas(self.fonte, self.textos[id_texto].texto, self.largura_texto)

    def mostrar(self, acao: AcaoDeEspera | None) -> None:
        """Chamada a cada quadro com a ação do diretor; prepara a caixa quando ela muda."""
        if acao is self._acao:
            return
        self._acao = acao
        self._selecionada = 0
        if isinstance(acao, Fala):
            self._linhas = self.linhas_da_fala(acao.id_texto)
            # A caixa cresce com o texto, para cobrir o mínimo da cena.
            linhas = max(len(self._linhas), MINIMO_DE_LINHAS)
            altura = linhas * self.altura_linha + 2 * RESPIRO
        elif isinstance(acao, Escolha):
            # ids-de-texto: dados (as opções vêm dos diálogos e da checagem)
            self._linhas = [self.textos[opcao].texto for opcao in acao.opcoes]
            altura = len(self._linhas) * self.altura_linha + 2 * RESPIRO
        else:
            self._linhas = []
            altura = 0
        largura = LARGURA_TELA - 2 * MARGEM
        self.retangulo = pygame.Rect(MARGEM, ALTURA_TELA - MARGEM - altura, largura, altura)

    @property
    def visivel(self) -> bool:
        return isinstance(self._acao, Fala | Escolha)

    def _opcao_em(self, posicao: tuple[int, int]) -> int | None:
        x, y = posicao
        if not self.retangulo.collidepoint(x, y):
            return None
        indice = (y - self.retangulo.y - RESPIRO) // self.altura_linha
        return indice if 0 <= indice < len(self._linhas) else None

    def tratar_evento(self, evento: pygame.Event) -> str | int | None:
        """`CONFIRMAR` numa fala, o índice escolhido numa escolha, ou `None`."""
        if isinstance(self._acao, Fala):
            if teclas.clique_esquerdo(evento) or (
                evento.type == pygame.KEYDOWN and evento.key in teclas.CONFIRMAR
            ):
                return CONFIRMAR
            return None
        if not isinstance(self._acao, Escolha):
            return None
        quantidade = len(self._linhas)
        if evento.type == pygame.KEYDOWN:
            if evento.key in teclas.CONFIRMAR:
                return self._selecionada
            if evento.key in teclas.ANTERIOR:
                self._selecionada = (self._selecionada - 1) % quantidade
            elif evento.key in teclas.PROXIMO:
                self._selecionada = (self._selecionada + 1) % quantidade
            elif (indice := teclas.numero(evento.key)) is not None and indice < quantidade:
                return indice
        elif evento.type == pygame.MOUSEMOTION:
            if (indice := self._opcao_em(evento.pos)) is not None:
                self._selecionada = indice
        elif teclas.clique_esquerdo(evento):
            return self._opcao_em(evento.pos)
        return None

    def desenhar(self, tela: pygame.Surface) -> None:
        if not self.visivel:
            return
        pygame.draw.rect(tela, Paleta.FUNDO, self.retangulo)
        pygame.draw.rect(tela, Paleta.TEXTO, self.retangulo, 1)
        x = self.retangulo.x + RESPIRO
        y = self.retangulo.y + RESPIRO
        escolha = isinstance(self._acao, Escolha)
        for indice, linha in enumerate(self._linhas):
            cor = Paleta.TEXTO
            if escolha:
                linha = f"{indice + 1}. {linha}"
                cor = Paleta.DESTAQUE if indice == self._selecionada else Paleta.TEXTO
            tela.blit(renderizar(self.fonte, linha, cor), (x, y))
            y += self.altura_linha
        if not escolha:
            # Seta no canto: a fala espera o jogador continuar.
            direita, baixo = self.retangulo.right - RESPIRO, self.retangulo.bottom - RESPIRO
            pontos = [(direita - 6, baixo - 4), (direita, baixo - 4), (direita - 3, baixo - 1)]
            pygame.draw.polygon(tela, Paleta.DESTAQUE, pontos)
