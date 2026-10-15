"""Tela do mapa: os locais liberados como retângulos com o nome (J1, I4).

Abre a partir da tela de cena (botão Mapa ou tecla M). Clique num local, ou Tab, setas e Enter,
para ir até ele; Esc volta para a cena sem sair do lugar. O local atual fica marcado.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from politicalizando.config import ALTURA_TELA, LARGURA_TELA, Paleta
from politicalizando.dominio.mapa import Local
from politicalizando.estados.base import Estado
from politicalizando.ui import teclas
from politicalizando.ui.texto import criar_fonte, quebrar_linhas, renderizar

if TYPE_CHECKING:
    from politicalizando.estados.cena import EstadoCena


class EstadoMapa(Estado):
    def __init__(self, tela_cena: EstadoCena) -> None:
        super().__init__(tela_cena.jogo)
        self.tela_cena = tela_cena
        self.partida = tela_cena.partida
        self.mapa = self.jogo.mapa
        self.fonte = criar_fonte()
        textos = self.jogo.textos
        self._titulo = renderizar(self.fonte, textos["mapa.titulo"].texto, Paleta.TEXTO)
        self._dica = renderizar(self.fonte, textos["mapa.dica"].texto, Paleta.APAGADO)
        locais = self.mapa.locais_liberados(self.partida.estado)
        atual = next((local for local in locais if local.cena == self.partida.cena.id), None)
        # O foco começa no local atual, para o Tab partir de onde você está.
        self.foco: str | None = atual.id if atual else None
        self.sob_mouse: str | None = None

    def _locais(self) -> tuple[Local, ...]:
        return self.mapa.locais_liberados(self.partida.estado)

    def ao_fechar(self) -> None:
        """Fechar a janela daqui salva como na cena (se nada estiver bloqueado)."""
        self.tela_cena.ao_fechar()

    def _voltar(self) -> None:
        self.jogo.trocar_estado(self.tela_cena)

    def _ir(self, local: Local) -> None:
        self.partida.ir_para(local.cena)
        self._voltar()

    def _mover_foco(self, passo: int) -> None:
        ids = [local.id for local in self._locais()]
        if self.foco not in ids:
            self.foco = ids[0] if passo > 0 else ids[-1]
        else:
            self.foco = ids[(ids.index(self.foco) + passo) % len(ids)]

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            tecla = evento.key
            if tecla in (pygame.K_ESCAPE, pygame.K_m):
                self._voltar()
            elif tecla == pygame.K_TAB:
                self._mover_foco(-1 if evento.mod & pygame.KMOD_SHIFT else 1)
            elif tecla in teclas.PROXIMO:
                self._mover_foco(1)
            elif tecla in teclas.ANTERIOR:
                self._mover_foco(-1)
            elif tecla in teclas.CONFIRMAR:
                local = next((loc for loc in self._locais() if loc.id == self.foco), None)
                if local is not None:
                    self._ir(local)
        elif evento.type == pygame.MOUSEMOTION:
            local = self.mapa.local_em(self.partida.estado, *evento.pos)
            self.sob_mouse = local.id if local else None
        elif teclas.clique_esquerdo(evento):
            local = self.mapa.local_em(self.partida.estado, *evento.pos)
            if local is not None:
                self._ir(local)

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        tela.blit(self._titulo, self._titulo.get_rect(midtop=(LARGURA_TELA // 2, 4)))
        tela.blit(self._dica, self._dica.get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - 2)))
        destacados = {self.foco, self.sob_mouse}
        for local in self._locais():
            area = pygame.Rect(local.area.x, local.area.y, local.area.largura, local.area.altura)
            atual = local.cena == self.partida.cena.id
            pygame.draw.rect(tela, Paleta.OBJETO, area)
            borda = Paleta.DESTAQUE if local.id in destacados else Paleta.APAGADO
            pygame.draw.rect(tela, borda, area, 2 if atual else 1)
            # ids-de-texto: dados (os nomes vêm do mapa.toml)
            nome = self.jogo.textos[local.nome].texto
            linhas = quebrar_linhas(self.fonte, nome, area.width - 4)
            y = area.centery - len(linhas) * self.fonte.get_linesize() // 2
            for linha in linhas:
                texto = renderizar(self.fonte, linha, Paleta.TEXTO)
                tela.blit(texto, texto.get_rect(midtop=(area.centerx, y)))
                y += self.fonte.get_linesize()
            if atual:
                # Marca "você está aqui": um losango no canto do local atual.
                x, y = area.right - 6, area.top + 6
                pontos = [(x, y - 3), (x + 3, y), (x, y + 3), (x - 3, y)]
                pygame.draw.polygon(tela, Paleta.DESTAQUE, pontos)
