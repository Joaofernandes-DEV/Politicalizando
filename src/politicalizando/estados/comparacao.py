"""Tela de comparação de propostas: uma proposta por vez, na ordem fixa das correntes (J5).

Abre por um roteiro (`{ abrir_tela = "comparacao" }`); o diretor espera até ela fechar. Teclado:
←/→ trocam a proposta, ↑/↓ e Page Up/Page Down rolam e Esc fecha. Mouse: as setas do cabeçalho
trocam a proposta, a roda rola. Não há resposta certa (C2): a tela só mostra prós, contras e
valores de cada uma.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from politicalizando.config import ALTURA_TELA, LARGURA_TELA, Cor, Paleta
from politicalizando.dominio.propostas import Proposta
from politicalizando.estados.base import Estado
from politicalizando.ui import teclas
from politicalizando.ui.texto import criar_fonte, quebrar_linhas, renderizar

if TYPE_CHECKING:
    from politicalizando.estados.cena import EstadoCena

Linha = tuple[str, Cor]
LARGURA_SETA = 16


class EstadoComparacao(Estado):
    def __init__(self, tela_cena: EstadoCena) -> None:
        super().__init__(tela_cena.jogo)
        self.tela_cena = tela_cena
        self.partida = tela_cena.partida
        self.fonte = criar_fonte()
        self.altura_linha = self.fonte.get_linesize()
        textos = self.jogo.textos
        self._titulo = textos["comparacao.titulo"].texto
        self._posicao = textos["comparacao.posicao"].texto
        self._secoes = (
            textos["comparacao.proposta"].texto,
            textos["comparacao.pros"].texto,
            textos["comparacao.contras"].texto,
            textos["comparacao.valores"].texto,
        )
        self._nomes = {
            "liberalismo": textos["corrente.liberalismo"].texto,
            "conservadorismo": textos["corrente.conservadorismo"].texto,
            "socialismo": textos["corrente.socialismo"].texto,
            "social_democracia": textos["corrente.social_democracia"].texto,
        }
        self._dica = renderizar(self.fonte, textos["comparacao.dica"].texto, Paleta.APAGADO)
        self._vazio = textos["comparacao.vazio"].texto
        self.seta_anterior = pygame.Rect(2, 2, LARGURA_SETA, self.altura_linha + 2)
        self.seta_proxima = pygame.Rect(
            LARGURA_TELA - 2 - LARGURA_SETA, 2, LARGURA_SETA, self.altura_linha + 2
        )
        largura = LARGURA_TELA - 8
        self._aviso = quebrar_linhas(self.fonte, textos["comparacao.aviso"].texto, largura)
        topo = self.seta_anterior.bottom + 2 + len(self._aviso) * self.altura_linha + 4
        self.area = pygame.Rect(4, topo, largura, ALTURA_TELA - topo - 16)
        self.propostas = self.jogo.propostas.liberadas(self.partida.estado)
        self.atual = 0
        self.rolagem = 0
        # Ver a comparação com duas ou mais propostas é uma ação de investigação (E1).
        self.jogo.propostas.registrar_comparacao(self.partida.estado)

    # --- Conteúdo ----------------------------------------------------------------------------

    def _paragrafo(self, texto: str, cor: Cor = Paleta.TEXTO, recuo: str = "") -> list[Linha]:
        linhas = quebrar_linhas(self.fonte, texto, self.area.width - self.fonte.size(recuo)[0])
        return [
            ((recuo if i == 0 else " " * len(recuo)) + linha, cor) for i, linha in enumerate(linhas)
        ]

    def _texto(self, id_texto: str) -> str:
        # ids-de-texto: dados (os IDs vêm do propostas.toml)
        return self.jogo.textos[id_texto].texto

    def cabecalho(self) -> str:
        if not self.propostas:
            return self._titulo
        proposta = self.propostas[self.atual]
        posicao = self._posicao.format(atual=self.atual + 1, total=len(self.propostas))
        return f"{self._nomes[proposta.corrente]} ({posicao})"

    def linhas(self) -> list[Linha]:
        if not self.propostas:
            return self._paragrafo(self._vazio, Paleta.APAGADO)
        proposta: Proposta = self.propostas[self.atual]
        linhas: list[Linha] = []
        grupos = ([proposta.proposta], proposta.pros, proposta.contras, proposta.valores)
        for titulo, ids in zip(self._secoes, grupos, strict=True):
            if linhas:
                linhas.append(("", Paleta.TEXTO))
            linhas += self._paragrafo(titulo, Paleta.DESTAQUE)
            # A proposta é um parágrafo; prós, contras e valores são listas.
            recuo = "" if titulo == self._secoes[0] else "- "
            for id_texto in ids:
                linhas += self._paragrafo(self._texto(id_texto), recuo=recuo)
        return linhas

    # --- Navegação ---------------------------------------------------------------------------

    @property
    def linhas_visiveis(self) -> int:
        return self.area.height // self.altura_linha

    def _rolar(self, passo: int) -> None:
        maximo = max(0, len(self.linhas()) - self.linhas_visiveis)
        self.rolagem = min(max(self.rolagem + passo, 0), maximo)

    def _trocar(self, passo: int) -> None:
        if self.propostas:
            self.atual = (self.atual + passo) % len(self.propostas)
            self.rolagem = 0

    def fechar(self) -> None:
        """Volta para a cena e deixa o roteiro que abriu a tela continuar."""
        self.partida.concluir_tela()
        self.jogo.trocar_estado(self.tela_cena)

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            tecla = evento.key
            if tecla == pygame.K_ESCAPE:
                self.fechar()
            elif tecla == pygame.K_LEFT:
                self._trocar(-1)
            elif tecla == pygame.K_RIGHT:
                self._trocar(1)
            elif tecla in (pygame.K_UP, pygame.K_DOWN):
                self._rolar(-1 if tecla == pygame.K_UP else 1)
            elif tecla in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                pagina = self.linhas_visiveis - 1
                self._rolar(-pagina if tecla == pygame.K_PAGEUP else pagina)
        elif evento.type == pygame.MOUSEWHEEL:
            self._rolar(-evento.y)
        elif teclas.clique_esquerdo(evento):
            if self.seta_anterior.collidepoint(evento.pos):
                self._trocar(-1)
            elif self.seta_proxima.collidepoint(evento.pos):
                self._trocar(1)

    # --- Desenho -----------------------------------------------------------------------------

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        cabecalho = renderizar(self.fonte, self.cabecalho(), Paleta.TEXTO)
        tela.blit(cabecalho, cabecalho.get_rect(midtop=(LARGURA_TELA // 2, 3)))
        if len(self.propostas) > 1:
            for botao, rotulo in ((self.seta_anterior, "<"), (self.seta_proxima, ">")):
                pygame.draw.rect(tela, Paleta.APAGADO, botao, 1)
                texto = renderizar(self.fonte, rotulo, Paleta.DESTAQUE)
                tela.blit(texto, texto.get_rect(center=botao.center))
        y = self.seta_anterior.bottom + 2
        for linha in self._aviso:
            texto = renderizar(self.fonte, linha, Paleta.APAGADO)
            tela.blit(texto, texto.get_rect(midtop=(LARGURA_TELA // 2, y)))
            y += self.altura_linha
        linhas = self.linhas()
        y = self.area.y
        for texto, cor in linhas[self.rolagem : self.rolagem + self.linhas_visiveis]:
            if texto.strip():
                tela.blit(renderizar(self.fonte, texto, cor), (self.area.x, y))
            y += self.altura_linha
        direita = self.area.right - 4
        if self.rolagem > 0:
            topo = self.area.y
            pontos = [(direita - 3, topo + 3), (direita + 3, topo + 3), (direita, topo)]
            pygame.draw.polygon(tela, Paleta.DESTAQUE, pontos)
        if self.rolagem + self.linhas_visiveis < len(linhas):
            baixo = self.area.bottom
            pontos = [(direita - 3, baixo - 3), (direita + 3, baixo - 3), (direita, baixo)]
            pygame.draw.polygon(tela, Paleta.DESTAQUE, pontos)
        tela.blit(self._dica, self._dica.get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - 2)))
