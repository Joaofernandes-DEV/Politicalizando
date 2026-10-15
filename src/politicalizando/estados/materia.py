"""Tela da matéria: escolher as peças, citar e entregar à editoria (J7, J11).

Abre por um roteiro (`{ abrir_tela = "materia" }`). Cada peça disponível tem duas caixas:
incluir na matéria e citar (a fonte de um fato, ou quem disse uma opinião). O tipo da peça não
aparece: separar fato, opinião e manipulação é a tarefa do jogador. Ao entregar, a editoria
comenta os três critérios, cada um com o nível e o que fazer melhor, sem nota única nem rótulo
(E1, E2). Dá para reescrever quantas vezes quiser; publicar marca `materia.publicou` e fecha.

Teclado: ↑/↓ escolhem a peça, ←/→ a caixa, Enter ou Espaço marcam, E entrega, Esc sai sem
entregar. No comentário: R ou Esc reescrevem, P publica. Mouse: clique nas caixas e nos botões,
roda para rolar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from politicalizando.config import ALTURA_TELA, LARGURA_TELA, Cor, Paleta
from politicalizando.dominio.materia import (
    Avaliacao,
    Inclusao,
    Nivel,
    TipoPeca,
    avaliar,
    pecas_disponiveis,
)
from politicalizando.dominio.materia import publicar as publicar_materia
from politicalizando.estados.base import Estado
from politicalizando.ui import teclas
from politicalizando.ui.texto import criar_fonte, quebrar_linhas, renderizar

if TYPE_CHECKING:
    from politicalizando.estados.cena import EstadoCena

INCLUIR, CITAR = 0, 1
LISTA, COMENTARIO = "lista", "comentario"
LADO_CAIXA = 7
RECUO = 12


@dataclass(frozen=True)
class Linha:
    texto: str
    cor: Cor = Paleta.TEXTO
    peca: int | None = None
    coluna: int | None = None
    # `None`: sem caixa; `True`/`False`: caixa marcada ou não.
    caixa: bool | None = None
    recuo: int = 0


class EstadoMateria(Estado):
    def __init__(self, tela_cena: EstadoCena) -> None:
        super().__init__(tela_cena.jogo)
        self.tela_cena = tela_cena
        self.partida = tela_cena.partida
        self.fonte = criar_fonte()
        self.altura_linha = self.fonte.get_linesize()
        textos = self.jogo.textos
        self._titulo = renderizar(self.fonte, textos["materia.titulo"].texto, Paleta.TEXTO)
        self._titulo_comentario = renderizar(
            self.fonte, textos["materia.comentario"].texto, Paleta.TEXTO
        )
        self._instrucao = textos["materia.instrucao"].texto
        self._vazio = textos["materia.vazio"].texto
        self._citar_fonte = textos["materia.citar_fonte"].texto
        self._citar_quem = textos["materia.citar_quem"].texto
        self._sem_fonte = textos["materia.sem_fonte"].texto
        self._sair = renderizar(self.fonte, textos["materia.dica"].texto, Paleta.APAGADO)
        self._criterios = {
            "fatos": textos["materia.criterio.fatos"].texto,
            "atribuicao": textos["materia.criterio.atribuicao"].texto,
            "justica": textos["materia.criterio.justica"].texto,
        }
        self._niveis = {
            Nivel.PRECISA_MELHORAR: textos["materia.nivel.precisa_melhorar"].texto,
            Nivel.EM_PARTE: textos["materia.nivel.em_parte"].texto,
            Nivel.BEM_FEITO: textos["materia.nivel.bem_feito"].texto,
        }
        self._explicacoes = {
            ("fatos", Nivel.BEM_FEITO): textos["materia.explica.fatos.bem_feito"].texto,
            ("fatos", Nivel.EM_PARTE): textos["materia.explica.fatos.em_parte"].texto,
            ("fatos", Nivel.PRECISA_MELHORAR): textos[
                "materia.explica.fatos.precisa_melhorar"
            ].texto,
            ("atribuicao", Nivel.BEM_FEITO): textos["materia.explica.atribuicao.bem_feito"].texto,
            ("atribuicao", Nivel.EM_PARTE): textos["materia.explica.atribuicao.em_parte"].texto,
            ("atribuicao", Nivel.PRECISA_MELHORAR): textos[
                "materia.explica.atribuicao.precisa_melhorar"
            ].texto,
            ("justica", Nivel.BEM_FEITO): textos["materia.explica.justica.bem_feito"].texto,
            ("justica", Nivel.EM_PARTE): textos["materia.explica.justica.em_parte"].texto,
            ("justica", Nivel.PRECISA_MELHORAR): textos[
                "materia.explica.justica.precisa_melhorar"
            ].texto,
        }
        # Botões no rodapé: Entregar na lista; Reescrever e Publicar no comentário.
        altura_botao = self.altura_linha + 2
        y_botoes = ALTURA_TELA - altura_botao - 2
        self.botao_entregar = self._botao(textos["materia.entregar"].texto, 4, y_botoes)
        self.botao_reescrever = self._botao(textos["materia.reescrever"].texto, 4, y_botoes)
        self.botao_publicar = self._botao(
            textos["materia.publicar"].texto, self.botao_reescrever[0].right + 6, y_botoes
        )
        largura = LARGURA_TELA - 8
        self._linhas_instrucao = quebrar_linhas(self.fonte, self._instrucao, largura)
        topo = 2 + self.altura_linha + len(self._linhas_instrucao) * self.altura_linha + 4
        self.area = pygame.Rect(4, topo, largura, y_botoes - topo - 4)

        self.disponiveis = pecas_disponiveis(self.jogo.pecas, self.partida.estado)
        self.incluidas: dict[str, bool] = {}  # peça → citar
        self.selecionada = 0
        self.coluna = INCLUIR
        self.rolagem = 0
        self.modo = LISTA
        self.avaliacao: Avaliacao | None = None

    def _botao(self, rotulo: str, x: int, y: int) -> tuple[pygame.Rect, str]:
        return pygame.Rect(x, y, self.fonte.size(rotulo)[0] + 8, self.altura_linha + 2), rotulo

    # --- Matéria -----------------------------------------------------------------------------

    def inclusoes(self) -> list[Inclusao]:
        """As peças incluídas, na ordem da lista."""
        return [
            Inclusao(peca.id, citar=self.incluidas[peca.id])
            for peca in self.disponiveis
            if peca.id in self.incluidas
        ]

    def alternar(self, indice: int, coluna: int) -> None:
        peca = self.disponiveis[indice]
        if coluna == INCLUIR:
            if peca.id in self.incluidas:
                del self.incluidas[peca.id]
            else:
                self.incluidas[peca.id] = False
        elif peca.pode_citar(self.partida.estado):
            # Citar inclui a peça; tirar a citação a mantém incluída.
            self.incluidas[peca.id] = not self.incluidas.get(peca.id, False)

    def entregar(self) -> None:
        self.avaliacao = avaliar(self.jogo.pecas, self.partida.estado, self.inclusoes())
        self.modo = COMENTARIO
        self.rolagem = 0

    def reescrever(self) -> None:
        self.modo = LISTA
        self.rolagem = 0

    def publicar(self) -> None:
        publicar_materia(self.jogo.pecas, self.partida.estado, self.inclusoes())
        self.fechar()

    def fechar(self) -> None:
        self.partida.concluir_tela()
        self.jogo.trocar_estado(self.tela_cena)

    # --- Linhas ------------------------------------------------------------------------------

    def _texto(self, id_texto: str) -> str:
        # ids-de-texto: dados (os textos das peças vêm do materia.toml)
        return self.jogo.textos[id_texto].texto

    def _quebrar(self, texto: str, recuo: int) -> list[str]:
        return quebrar_linhas(self.fonte, texto, self.area.width - recuo)

    def linhas(self) -> list[Linha]:
        if self.modo == COMENTARIO:
            return self._linhas_do_comentario()
        if not self.disponiveis:
            return [Linha(t, Paleta.APAGADO) for t in self._quebrar(self._vazio, 0)]
        linhas: list[Linha] = []
        estado = self.partida.estado
        for indice, peca in enumerate(self.disponiveis):
            if linhas:
                linhas.append(Linha(""))
            focada = indice == self.selecionada
            incluida = peca.id in self.incluidas
            cor = Paleta.DESTAQUE if focada and self.coluna == INCLUIR else Paleta.TEXTO
            for numero, texto in enumerate(self._quebrar(self._texto(peca.texto), RECUO)):
                caixa = incluida if numero == 0 else None
                linhas.append(Linha(texto, cor, indice, INCLUIR, caixa, RECUO))
            recuo = 2 * RECUO
            if peca.pode_citar(estado):
                rotulo = self._citar_quem if peca.tipo is TipoPeca.OPINIAO else self._citar_fonte
                cor = Paleta.DESTAQUE if focada and self.coluna == CITAR else Paleta.TEXTO
                caixa = self.incluidas.get(peca.id, False)
            else:
                rotulo, cor, caixa = f"({self._sem_fonte})", Paleta.APAGADO, None
            for numero, texto in enumerate(self._quebrar(rotulo, recuo)):
                linhas.append(
                    Linha(texto, cor, indice, CITAR, caixa if numero == 0 else None, recuo)
                )
        return linhas

    def _linhas_do_comentario(self) -> list[Linha]:
        avaliacao = self.avaliacao
        niveis = {"fatos": avaliacao.fatos, "atribuicao": avaliacao.atribuicao}
        niveis["justica"] = avaliacao.justica
        linhas: list[Linha] = []
        for criterio, nivel in niveis.items():
            if linhas:
                linhas.append(Linha(""))
            titulo = f"{self._criterios[criterio]}: {self._niveis[nivel]}"
            linhas += [Linha(t, Paleta.DESTAQUE) for t in self._quebrar(titulo, 0)]
            explicacao = self._explicacoes[(criterio, nivel)]
            linhas += [Linha(t) for t in self._quebrar(explicacao, 0)]
        return linhas

    # --- Navegação ---------------------------------------------------------------------------

    @property
    def linhas_visiveis(self) -> int:
        return self.area.height // self.altura_linha

    def _rolar(self, passo: int) -> None:
        maximo = max(0, len(self.linhas()) - self.linhas_visiveis)
        self.rolagem = min(max(self.rolagem + passo, 0), maximo)

    def _mostrar_selecionada(self) -> None:
        indices = [
            i
            for i, linha in enumerate(self.linhas())
            if linha.peca == self.selecionada and linha.coluna == self.coluna
        ]
        if not indices:
            return
        if indices[0] < self.rolagem:
            self.rolagem = indices[0]
        elif indices[-1] >= self.rolagem + self.linhas_visiveis:
            self.rolagem = indices[-1] - self.linhas_visiveis + 1

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.MOUSEWHEEL:
            self._rolar(-evento.y)
        elif self.modo == COMENTARIO:
            self._evento_do_comentario(evento)
        elif evento.type == pygame.KEYDOWN:
            self._tecla_da_lista(evento.key)
        elif teclas.clique_esquerdo(evento):
            if self.botao_entregar[0].collidepoint(evento.pos):
                self.entregar()
            elif self.area.collidepoint(evento.pos):
                indice = (evento.pos[1] - self.area.y) // self.altura_linha + self.rolagem
                linhas = self.linhas()
                if 0 <= indice < len(linhas) and linhas[indice].peca is not None:
                    linha = linhas[indice]
                    self.selecionada, self.coluna = linha.peca, linha.coluna
                    self.alternar(linha.peca, linha.coluna)

    def _tecla_da_lista(self, tecla: int) -> None:
        if tecla == pygame.K_ESCAPE:
            self.fechar()
        elif tecla == pygame.K_e:
            self.entregar()
        elif not self.disponiveis:
            return
        elif tecla in (pygame.K_UP, pygame.K_DOWN):
            passo = -1 if tecla == pygame.K_UP else 1
            self.selecionada = min(max(self.selecionada + passo, 0), len(self.disponiveis) - 1)
            self._mostrar_selecionada()
        elif tecla in (pygame.K_LEFT, pygame.K_RIGHT):
            self.coluna = INCLUIR if tecla == pygame.K_LEFT else CITAR
            self._mostrar_selecionada()
        elif tecla in teclas.CONFIRMAR:
            self.alternar(self.selecionada, self.coluna)

    def _evento_do_comentario(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_r, pygame.K_ESCAPE):
                self.reescrever()
            elif evento.key == pygame.K_p:
                self.publicar()
            elif evento.key in (pygame.K_UP, pygame.K_DOWN):
                self._rolar(-1 if evento.key == pygame.K_UP else 1)
        elif teclas.clique_esquerdo(evento):
            if self.botao_reescrever[0].collidepoint(evento.pos):
                self.reescrever()
            elif self.botao_publicar[0].collidepoint(evento.pos):
                self.publicar()

    # --- Desenho -----------------------------------------------------------------------------

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        titulo = self._titulo if self.modo == LISTA else self._titulo_comentario
        tela.blit(titulo, titulo.get_rect(midtop=(LARGURA_TELA // 2, 2)))
        y = 2 + self.altura_linha
        if self.modo == LISTA:
            for linha in self._linhas_instrucao:
                texto = renderizar(self.fonte, linha, Paleta.APAGADO)
                tela.blit(texto, texto.get_rect(midtop=(LARGURA_TELA // 2, y)))
                y += self.altura_linha
        linhas = self.linhas()
        y = self.area.y
        for linha in linhas[self.rolagem : self.rolagem + self.linhas_visiveis]:
            x = self.area.x + linha.recuo
            if linha.caixa is not None:
                caixa = pygame.Rect(x - RECUO + 1, y + 2, LADO_CAIXA, LADO_CAIXA)
                pygame.draw.rect(tela, linha.cor, caixa, 1)
                if linha.caixa:
                    pygame.draw.rect(tela, linha.cor, caixa.inflate(-4, -4))
            if linha.texto:
                tela.blit(renderizar(self.fonte, linha.texto, linha.cor), (x, y))
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
        botoes = (
            [self.botao_entregar]
            if self.modo == LISTA
            else [
                self.botao_reescrever,
                self.botao_publicar,
            ]
        )
        for botao, rotulo in botoes:
            pygame.draw.rect(tela, Paleta.TEXTO, botao, 1)
            texto = renderizar(self.fonte, rotulo, Paleta.TEXTO)
            tela.blit(texto, texto.get_rect(center=botao.center))
        if self.modo == LISTA:
            tela.blit(
                self._sair, self._sair.get_rect(bottomright=(LARGURA_TELA - 4, ALTURA_TELA - 3))
            )
