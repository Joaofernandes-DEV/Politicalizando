"""Tela de título provisória: Novo jogo, Continuar (se houver save) e Esc para sair.

Teclado: ↑/↓ escolhem e Enter ou Espaço confirmam; 1 e 2 escolhem direto (I4). Mouse: clique.

O visual final e os outros menus (como jogar, créditos) são da Fase 3 (I7).
"""

from __future__ import annotations

from collections.abc import Callable

import pygame

from politicalizando import __version__
from politicalizando.config import LARGURA_TELA, TITULO, Paleta
from politicalizando.dominio.estado_jogo import SaveInvalido
from politicalizando.dominio.partida import Partida
from politicalizando.estados.base import Estado
from politicalizando.estados.cena import EstadoCena
from politicalizando.jogo import Jogo
from politicalizando.persistencia import carregar, existe_save
from politicalizando.ui import teclas
from politicalizando.ui.texto import criar_fonte, quebrar_linhas, renderizar

Y_OPCOES = 94
LARGURA_AVISO = LARGURA_TELA - 16


class EstadoTitulo(Estado):
    def __init__(self, jogo: Jogo, aviso: str | None = None) -> None:
        """`aviso` é um texto já resolvido (ex.: o save falhou ao sair da cena)."""
        super().__init__(jogo)
        # Fonte padrão do pygame até a fonte pixel com acentos chegar (Fase 3, I2).
        fonte_titulo = pygame.font.Font(None, 28)
        self.fonte = criar_fonte()
        textos = jogo.textos
        self._linhas = [
            (fonte_titulo.render(TITULO.upper(), False, Paleta.DESTAQUE), 44),
            (renderizar(self.fonte, textos["titulo.frase"].texto, Paleta.TEXTO), 72),
            (renderizar(self.fonte, textos["titulo.dica_sair"].texto, Paleta.APAGADO), 152),
            (renderizar(self.fonte, f"v{__version__}", Paleta.APAGADO), 166),
        ]
        self.opcoes: list[tuple[str, Callable[[], None]]] = [
            (textos["titulo.novo_jogo"].texto, self._novo_jogo)
        ]
        if existe_save():
            self.opcoes.append((textos["titulo.continuar"].texto, self._continuar))
        self.selecionada = 0
        self.aviso = aviso
        altura = self.fonte.get_linesize() + 2
        self._botoes = []
        for indice, (rotulo, _) in enumerate(self.opcoes):
            botao = pygame.Rect(0, 0, self.fonte.size(rotulo)[0] + 8, altura)
            botao.midtop = (LARGURA_TELA // 2, Y_OPCOES + indice * altura)
            self._botoes.append(botao)

    def _novo_jogo(self) -> None:
        # O save antigo só é substituído no primeiro autosave do jogo novo.
        self.jogo.trocar_estado(EstadoCena(self.jogo, Partida.nova(self.jogo.interacao)))

    def _continuar(self) -> None:
        try:
            estado = carregar()
            if estado is None:
                self._novo_jogo()
                return
            partida = Partida(estado, self.jogo.interacao)
        except (SaveInvalido, OSError):
            # O arquivo nunca é apagado: quem joga decide o que fazer com ele.
            self.aviso = self.jogo.textos["titulo.save_invalido"].texto
            return
        self.jogo.trocar_estado(EstadoCena(self.jogo, partida))

    def _botao_em(self, posicao: tuple[int, int]) -> int | None:
        return next(
            (indice for indice, botao in enumerate(self._botoes) if botao.collidepoint(posicao)),
            None,
        )

    def _escolher(self, indice: int) -> None:
        self.aviso = None
        self.opcoes[indice][1]()

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.jogo.encerrar()
            elif evento.key in teclas.CONFIRMAR:
                self._escolher(self.selecionada)
            elif evento.key in teclas.ANTERIOR:
                self.selecionada = (self.selecionada - 1) % len(self.opcoes)
            elif evento.key in teclas.PROXIMO:
                self.selecionada = (self.selecionada + 1) % len(self.opcoes)
            elif (indice := teclas.numero(evento.key)) is not None and indice < len(self.opcoes):
                self._escolher(indice)
        elif evento.type == pygame.MOUSEMOTION:
            if (indice := self._botao_em(evento.pos)) is not None:
                self.selecionada = indice
        elif teclas.clique_esquerdo(evento) and (indice := self._botao_em(evento.pos)) is not None:
            self._escolher(indice)

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        for superficie, y in self._linhas:
            tela.blit(superficie, superficie.get_rect(midtop=(LARGURA_TELA // 2, y)))
        for indice, ((rotulo, _), botao) in enumerate(zip(self.opcoes, self._botoes, strict=True)):
            cor = Paleta.DESTAQUE if indice == self.selecionada else Paleta.TEXTO
            texto = renderizar(self.fonte, rotulo, cor)
            tela.blit(texto, texto.get_rect(center=botao.center))
        if self.aviso:
            y = Y_OPCOES + len(self._botoes) * (self.fonte.get_linesize() + 2) + 4
            for linha in quebrar_linhas(self.fonte, self.aviso, LARGURA_AVISO):
                texto = renderizar(self.fonte, linha, Paleta.DESTAQUE)
                tela.blit(texto, texto.get_rect(midtop=(LARGURA_TELA // 2, y)))
                y += self.fonte.get_linesize()
