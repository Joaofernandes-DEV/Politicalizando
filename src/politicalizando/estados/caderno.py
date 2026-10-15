"""Tela do caderno: fichas, conversas, fontes e itens, em abas (J3, J6, J13).

Abre a partir da tela de cena (botão Caderno ou tecla C). Teclado: ←/→ ou 1 a 4 trocam a aba,
↑/↓ rolam (ou escolhem a ficha), Page Up/Page Down rolam uma página, Enter abre a ficha e Esc
fecha a ficha ou o caderno; C também fecha. Mouse: clique na aba ou na ficha e roda para rolar.
Tudo aparece na ordem fixa dos dados: as fichas, na ordem das correntes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from politicalizando.config import ALTURA_TELA, LARGURA_TELA, Cor, Paleta
from politicalizando.dominio.caderno import Entrada, Origem
from politicalizando.dominio.fichas import Ficha
from politicalizando.dominio.fontes import Fonte
from politicalizando.estados.base import Estado
from politicalizando.ui import teclas
from politicalizando.ui.texto import criar_fonte, quebrar_linhas, renderizar

if TYPE_CHECKING:
    from politicalizando.estados.cena import EstadoCena

FICHAS, CONVERSAS, FONTES, ITENS = range(4)
Linha = tuple[str, Cor]


class EstadoCaderno(Estado):
    def __init__(self, tela_cena: EstadoCena) -> None:
        super().__init__(tela_cena.jogo)
        self.tela_cena = tela_cena
        self.estado_jogo = tela_cena.partida.estado
        self.caderno = self.jogo.caderno
        self.fichas = self.jogo.fichas
        self.fonte = criar_fonte()
        self.altura_linha = self.fonte.get_linesize()
        textos = self.jogo.textos
        self._abas = [
            textos["caderno.aba.fichas"].texto,
            textos["caderno.aba.conversas"].texto,
            textos["caderno.aba.fontes"].texto,
            textos["caderno.aba.itens"].texto,
        ]
        self.botoes_abas: list[pygame.Rect] = []
        x = 4
        for rotulo in self._abas:
            botao = pygame.Rect(x, 2, self.fonte.size(rotulo)[0] + 8, self.altura_linha + 2)
            self.botoes_abas.append(botao)
            x = botao.right + 2
        topo = self.botoes_abas[0].bottom + 4
        self.area = pygame.Rect(4, topo, LARGURA_TELA - 8, ALTURA_TELA - topo - 16)
        self._dica = renderizar(self.fonte, textos["caderno.dica"].texto, Paleta.APAGADO)
        self._vazio = textos["caderno.vazio"].texto
        self._nomes = {
            "liberalismo": textos["corrente.liberalismo"].texto,
            "conservadorismo": textos["corrente.conservadorismo"].texto,
            "socialismo": textos["corrente.socialismo"].texto,
            "social_democracia": textos["corrente.social_democracia"].texto,
            "outras": textos["corrente.outras"].texto,
        }
        self._origens = {
            Origem.FATO: textos["caderno.origem.fato"].texto,
            Origem.INTERPRETACAO: textos["caderno.origem.interpretacao"].texto,
        }
        self.aba = FICHAS
        self.rolagem = 0
        self.selecionada = 0
        self.ficha_aberta: Ficha | None = None

    # --- Conteúdo ----------------------------------------------------------------------------

    def _texto(self, id_texto: str) -> str:
        # ids-de-texto: dados (os IDs vêm do caderno.toml e do fichas.toml)
        return self.jogo.textos[id_texto].texto

    def _paragrafo(self, texto: str, cor: Cor = Paleta.TEXTO) -> list[Linha]:
        return [(linha, cor) for linha in quebrar_linhas(self.fonte, texto, self.area.width)]

    def _descrever_fonte(self, fonte: Fonte) -> str:
        partes = [fonte.autor, fonte.titulo]
        if fonte.editora:
            partes.append(fonte.editora)
        descricao = ". ".join(partes) + f", {fonte.ano}."
        if fonte.url:
            acesso = self.jogo.textos["caderno.fonte.acesso"].texto
            descricao += f" {fonte.url} ({acesso} {fonte.acesso:%d/%m/%Y})."
        if fonte.do_jogo:
            descricao += f" ({self.jogo.textos['caderno.fonte.do_jogo'].texto})"
        return descricao

    def fichas_desbloqueadas(self) -> tuple[Ficha, ...]:
        return self.fichas.desbloqueadas(self.estado_jogo)

    def linhas(self) -> list[Linha]:
        """As linhas da aba (ou da ficha aberta), já quebradas na largura da área."""
        if self.ficha_aberta is not None:
            return self._linhas_da_ficha(self.ficha_aberta)
        if self.aba == FICHAS:
            linhas = [
                (
                    self._nomes[ficha.corrente],
                    Paleta.DESTAQUE if i == self.selecionada else Paleta.TEXTO,
                )
                for i, ficha in enumerate(self.fichas_desbloqueadas())
            ]
        elif self.aba == CONVERSAS:
            linhas = self._linhas_das_entradas(self.caderno.conversas(self.estado_jogo))
        elif self.aba == FONTES:
            linhas = self._linhas_das_entradas(self.caderno.fontes(self.estado_jogo))
        else:
            itens = self.caderno.itens_do_inventario(self.estado_jogo)
            linhas = [(self._texto(item), Paleta.TEXTO) for item in itens]
        return linhas or self._paragrafo(self._vazio, Paleta.APAGADO)

    def _linhas_das_entradas(self, entradas: tuple[Entrada, ...]) -> list[Linha]:
        linhas: list[Linha] = []
        for entrada in entradas:
            if linhas:
                linhas.append(("", Paleta.TEXTO))
            if entrada.origem is Origem.OPINIAO:
                titulo = self._texto(entrada.de)
            else:
                titulo = self._origens[entrada.origem]
            linhas += self._paragrafo(titulo, Paleta.DESTAQUE)
            linhas += self._paragrafo(self._texto(entrada.texto))
            for fonte in entrada.fontes:
                linhas += self._paragrafo(self._descrever_fonte(fonte), Paleta.APAGADO)
        return linhas

    def _linhas_da_ficha(self, ficha: Ficha) -> list[Linha]:
        textos = self.jogo.textos
        secoes: list[tuple[str, list[str]]] = [
            (textos["ficha.item.ideia_central"].texto, [ficha.ideia_central]),
            (textos["ficha.item.valores"].texto, list(ficha.valores)),
            (textos["ficha.item.estado"].texto, [ficha.estado]),
            (textos["ficha.item.mercado"].texto, [ficha.mercado]),
            (textos["ficha.item.sociedade"].texto, [ficha.sociedade]),
            (textos["ficha.item.origem"].texto, [ficha.origem]),
            (textos["ficha.item.pensadores"].texto, list(ficha.pensadores)),
            (textos["ficha.item.proposta"].texto, [ficha.proposta]),
        ]
        linhas = self._paragrafo(self._nomes[ficha.corrente], Paleta.DESTAQUE)
        for titulo, ids in secoes:
            linhas += [("", Paleta.TEXTO), *self._paragrafo(titulo, Paleta.APAGADO)]
            for id_texto in ids:
                linhas += self._paragrafo(self._texto(id_texto))
        linhas += [("", Paleta.TEXTO)]
        linhas += self._paragrafo(textos["ficha.item.criticas"].texto, Paleta.APAGADO)
        critica_de = textos["ficha.item.critica_de"].texto
        for critica in ficha.criticas:
            linhas += self._paragrafo(f"{critica_de} {self._nomes[critica.de]}", Paleta.DESTAQUE)
            linhas += self._paragrafo(self._texto(critica.texto))
        for titulo, ids in (
            (textos["ficha.item.confusoes"].texto, ficha.confusoes),
            (textos["ficha.item.diferencas_internas"].texto, ficha.diferencas_internas),
        ):
            linhas += [("", Paleta.TEXTO), *self._paragrafo(titulo, Paleta.APAGADO)]
            for id_texto in ids:
                linhas += self._paragrafo(self._texto(id_texto))
        linhas += [("", Paleta.TEXTO)]
        linhas += self._paragrafo(textos["ficha.item.fontes"].texto, Paleta.APAGADO)
        for fonte in ficha.fontes:
            linhas += self._paragrafo(self._descrever_fonte(fonte))
        return linhas

    # --- Rolagem e navegação -----------------------------------------------------------------

    @property
    def linhas_visiveis(self) -> int:
        return self.area.height // self.altura_linha

    def _rolar(self, passo: int) -> None:
        maximo = max(0, len(self.linhas()) - self.linhas_visiveis)
        self.rolagem = min(max(self.rolagem + passo, 0), maximo)

    def _trocar_aba(self, aba: int) -> None:
        self.aba = aba % len(self._abas)
        self.rolagem = self.selecionada = 0
        self.ficha_aberta = None

    def _selecionar(self, passo: int) -> None:
        fichas = self.fichas_desbloqueadas()
        if not fichas:
            return
        self.selecionada = (self.selecionada + passo) % len(fichas)
        # Mantém a ficha escolhida dentro da área visível.
        if self.selecionada < self.rolagem:
            self.rolagem = self.selecionada
        elif self.selecionada >= self.rolagem + self.linhas_visiveis:
            self.rolagem = self.selecionada - self.linhas_visiveis + 1

    def _abrir_ficha(self, indice: int) -> None:
        fichas = self.fichas_desbloqueadas()
        if 0 <= indice < len(fichas):
            self.selecionada = indice
            self.ficha_aberta = fichas[indice]
            self.rolagem = 0

    def _voltar(self) -> None:
        self.jogo.trocar_estado(self.tela_cena)

    @property
    def _na_lista_de_fichas(self) -> bool:
        return self.aba == FICHAS and self.ficha_aberta is None

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            self._tecla(evento.key)
        elif evento.type == pygame.MOUSEWHEEL:
            self._rolar(-evento.y)
        elif teclas.clique_esquerdo(evento):
            aba = next(
                (i for i, b in enumerate(self.botoes_abas) if b.collidepoint(evento.pos)), None
            )
            if aba is not None:
                self._trocar_aba(aba)
            elif self._na_lista_de_fichas and self.area.collidepoint(evento.pos):
                linha = (evento.pos[1] - self.area.y) // self.altura_linha + self.rolagem
                self._abrir_ficha(linha)

    def _tecla(self, tecla: int) -> None:
        if tecla == pygame.K_ESCAPE:
            if self.ficha_aberta is not None:
                self.ficha_aberta = None
                self.rolagem = 0
            else:
                self._voltar()
        elif tecla == pygame.K_c:
            self._voltar()
        elif tecla == pygame.K_LEFT:
            self._trocar_aba(self.aba - 1)
        elif tecla == pygame.K_RIGHT:
            self._trocar_aba(self.aba + 1)
        elif (indice := teclas.numero(tecla)) is not None and indice < len(self._abas):
            self._trocar_aba(indice)
        elif tecla in (pygame.K_UP, pygame.K_DOWN):
            passo = -1 if tecla == pygame.K_UP else 1
            if self._na_lista_de_fichas:
                self._selecionar(passo)
            else:
                self._rolar(passo)
        elif tecla in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
            pagina = self.linhas_visiveis - 1
            self._rolar(-pagina if tecla == pygame.K_PAGEUP else pagina)
        elif tecla in teclas.CONFIRMAR and self._na_lista_de_fichas:
            self._abrir_ficha(self.selecionada)

    # --- Desenho -----------------------------------------------------------------------------

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        for indice, (rotulo, botao) in enumerate(zip(self._abas, self.botoes_abas, strict=True)):
            cor = Paleta.DESTAQUE if indice == self.aba else Paleta.APAGADO
            pygame.draw.rect(tela, cor, botao, 1)
            texto = renderizar(self.fonte, rotulo, cor)
            tela.blit(texto, texto.get_rect(center=botao.center))
        linhas = self.linhas()
        y = self.area.y
        for texto, cor in linhas[self.rolagem : self.rolagem + self.linhas_visiveis]:
            if texto:
                tela.blit(renderizar(self.fonte, texto, cor), (self.area.x, y))
            y += self.altura_linha
        # Setas na borda direita quando há mais texto acima ou abaixo.
        direita = self.area.right - 4
        if self.rolagem > 0:
            topo = self.area.y
            pygame.draw.polygon(
                tela,
                Paleta.DESTAQUE,
                [(direita - 3, topo + 3), (direita + 3, topo + 3), (direita, topo)],
            )
        if self.rolagem + self.linhas_visiveis < len(linhas):
            baixo = self.area.bottom
            pygame.draw.polygon(
                tela,
                Paleta.DESTAQUE,
                [(direita - 3, baixo - 3), (direita + 3, baixo - 3), (direita, baixo)],
            )
        tela.blit(self._dica, self._dica.get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - 2)))
