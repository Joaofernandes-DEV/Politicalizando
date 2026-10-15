"""Tela de cena: objetos como retângulos, menu de verbos e caixa de diálogo (D8, I4, I9).

As regras da partida (input bloqueado, entrada da cena, hora do autosave) ficam em
`dominio/partida.py`; aqui só se desenha e se traduz o input:

- mouse: o objeto sob o cursor fica destacado e mostra o nome; o clique abre o menu de verbos;
- teclado: Tab, Shift+Tab e as setas percorrem os objetos, Enter ou Espaço abrem o menu, 1, 2 e
  3 usam um verbo direto e Esc volta ao título (salvando, se nada estiver bloqueado);
- mostrar objetos: a tecla O liga e desliga o destaque de todos os objetos visíveis, com o nome
  de cada um junto do retângulo (I8). Vale para todas as cenas até ser desligado e some durante
  as falas e com o menu de verbos aberto, para não cobrir a caixa;
- mapa: depois de liberado, o botão Mapa no canto e a tecla M abrem o mapa (J1);
- caderno: o botão Caderno no canto e a tecla C abrem o caderno, desde o início (J6).

Quando um roteiro pede `AbrirTela`, a tela de cena abre a tela pedida (ex.: a comparação de
propostas); ao fechar, ela devolve a vez à cena e o roteiro continua.

Enquanto a partida está ocupada, o input vai só para a caixa de diálogo. Fechar a janela salva
como o Esc (`ao_fechar`).
"""

from __future__ import annotations

import pygame

from politicalizando.config import LARGURA_TELA, Paleta
from politicalizando.dominio.acoes import AbrirTela, Fala
from politicalizando.dominio.cenas import Objeto, Verbo
from politicalizando.dominio.partida import Partida
from politicalizando.estados.base import Estado
from politicalizando.estados.caderno import EstadoCaderno
from politicalizando.estados.comparacao import EstadoComparacao
from politicalizando.estados.mapa import EstadoMapa
from politicalizando.estados.materia import EstadoMateria
from politicalizando.jogo import Jogo
from politicalizando.persistencia import autosalvar
from politicalizando.ui import rotulos, teclas
from politicalizando.ui.caixa_dialogo import CONFIRMAR, CaixaDialogo
from politicalizando.ui.menu_verbos import MenuVerbos
from politicalizando.ui.texto import criar_fonte, renderizar

# As telas que um roteiro pode abrir (`AbrirTela`).
TELAS = {"comparacao": EstadoComparacao, "materia": EstadoMateria}

# Na ordem das teclas 1, 2 e 3, a mesma do menu.
VERBOS = (Verbo.OLHAR, Verbo.USAR, Verbo.FALAR)


class EstadoCena(Estado):
    def __init__(self, jogo: Jogo, partida: Partida) -> None:
        super().__init__(jogo)
        self.partida = partida
        self.fonte = criar_fonte()
        self.caixa = CaixaDialogo(self.fonte, jogo.textos)
        self.menu = MenuVerbos(self.fonte, jogo.textos)
        # IDs dos objetos com o foco do teclado, sob o mouse e com o menu aberto.
        self.foco: str | None = None
        self.sob_mouse: str | None = None
        self._menu_de: str | None = None
        self._cena: str | None = None
        # Botões no canto de cima: o Caderno na ponta e o Mapa ao lado dele.
        textos = jogo.textos
        self._rotulo_caderno = renderizar(self.fonte, textos["caderno.botao"].texto, Paleta.TEXTO)
        self.botao_caderno = self._rotulo_caderno.get_rect().inflate(8, 2)
        self.botao_caderno.topright = (LARGURA_TELA - 2, 2)
        self._rotulo_mapa = renderizar(self.fonte, textos["mapa.botao"].texto, Paleta.TEXTO)
        self.botao_mapa = self._rotulo_mapa.get_rect().inflate(8, 2)
        self.botao_mapa.topright = (self.botao_caderno.left - 2, 2)

    # --- Input -------------------------------------------------------------------------------

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.MOUSEMOTION:
            objeto = self.partida.objeto_em(*evento.pos)
            self.sob_mouse = objeto.id if objeto else None
        if self.partida.ocupada:
            self._responder_caixa(evento)
        elif self.menu.aberto:
            verbo = self.menu.tratar_evento(evento)
            if isinstance(verbo, Verbo):
                self._agir(self._menu_de, verbo)
        elif evento.type == pygame.KEYDOWN:
            self._tecla(evento)
        elif (
            teclas.clique_esquerdo(evento)
            and self.mapa_liberado
            and self.botao_mapa.collidepoint(evento.pos)
        ):
            self._abrir_mapa()
        elif teclas.clique_esquerdo(evento) and self.botao_caderno.collidepoint(evento.pos):
            self._abrir_caderno()
        elif teclas.clique_esquerdo(evento):
            objeto = self.partida.objeto_em(*evento.pos)
            if objeto is not None:
                self.foco = objeto.id
                self._abrir_menu(objeto)

    def _responder_caixa(self, evento: pygame.Event) -> None:
        self.caixa.mostrar(self.partida.diretor.acao_atual)
        resposta = self.caixa.tratar_evento(evento)
        if resposta == CONFIRMAR:
            self.partida.confirmar()
        elif isinstance(resposta, int):
            self.partida.escolher(resposta)

    def _tecla(self, evento: pygame.Event) -> None:
        tecla = evento.key
        if tecla == pygame.K_ESCAPE:
            self._voltar_ao_titulo()
        elif tecla == pygame.K_m:
            if self.mapa_liberado:
                self._abrir_mapa()
        elif tecla == pygame.K_c:
            self._abrir_caderno()
        elif tecla == pygame.K_o:
            self.jogo.mostrar_objetos = not self.jogo.mostrar_objetos
        elif tecla == pygame.K_TAB:
            self._mover_foco(-1 if evento.mod & pygame.KMOD_SHIFT else 1)
        elif tecla in teclas.PROXIMO:
            self._mover_foco(1)
        elif tecla in teclas.ANTERIOR:
            self._mover_foco(-1)
        elif tecla in teclas.CONFIRMAR:
            if (objeto := self._objeto_em_foco()) is not None:
                self._abrir_menu(objeto)
        elif (
            (indice := teclas.numero(tecla)) is not None
            and indice < len(VERBOS)
            and (objeto := self._objeto_em_foco()) is not None
        ):
            self._agir(objeto.id, VERBOS[indice])

    @property
    def mapa_liberado(self) -> bool:
        """O botão e a tecla do mapa só valem com o mapa liberado e nada em andamento."""
        return not self.partida.ocupada and self.jogo.mapa.liberado(self.partida.estado)

    @property
    def mostrando_objetos(self) -> bool:
        """O destaque de todos os objetos está ligado e não cobre a caixa nem o menu."""
        return self.jogo.mostrar_objetos and not self.partida.ocupada and not self.menu.aberto

    def _abrir_mapa(self) -> None:
        self.menu.fechar()
        self.jogo.trocar_estado(EstadoMapa(self))

    def _abrir_caderno(self) -> None:
        self.menu.fechar()
        self.jogo.trocar_estado(EstadoCaderno(self))

    def _objeto_em_foco(self) -> Objeto | None:
        """O objeto com o foco; sem foco, o primeiro da cena (Enter já funciona de cara)."""
        objetos = self.partida.objetos()
        if self.foco is None and objetos:
            self.foco = objetos[0].id
        return next((objeto for objeto in objetos if objeto.id == self.foco), None)

    def _mover_foco(self, passo: int) -> None:
        ids = [objeto.id for objeto in self.partida.objetos()]
        if not ids:
            return
        if self.foco not in ids:
            self.foco = ids[0] if passo > 0 else ids[-1]
        else:
            self.foco = ids[(ids.index(self.foco) + passo) % len(ids)]

    def _abrir_menu(self, objeto: Objeto) -> None:
        self._menu_de = objeto.id
        self.menu.abrir(objeto.area)

    def _agir(self, id_objeto: str | None, verbo: Verbo) -> None:
        objeto = next((obj for obj in self.partida.objetos() if obj.id == id_objeto), None)
        if objeto is not None:
            self.partida.agir(objeto, verbo)

    # --- Save e saída ------------------------------------------------------------------------

    def _salvar(self) -> bool:
        """Autosave (D10); devolve `False` se a pasta não deixou gravar."""
        try:
            autosalvar(self.partida.estado, bloqueado=self.partida.ocupada)
        except OSError:
            return False
        return True

    def ao_fechar(self) -> None:
        """Fechar a janela salva como o Esc; se a gravação falhar, a janela fecha assim mesmo."""
        self._salvar()

    def _voltar_ao_titulo(self) -> None:
        from politicalizando.estados.titulo import EstadoTitulo

        aviso = None if self._salvar() else self.jogo.textos["aviso.save_falhou"].texto
        self.jogo.trocar_estado(EstadoTitulo(self.jogo, aviso=aviso))

    # --- Quadro ------------------------------------------------------------------------------

    def atualizar(self, dt: float) -> None:
        if self.partida.atualizar(dt) and not self._salvar():
            self.partida.avisar(Fala("aviso.save_falhou"))
        if self.partida.cena.id != self._cena:
            self._cena = self.partida.cena.id
            self.foco = self.sob_mouse = self._menu_de = None
            self.menu.fechar()
        ids = {objeto.id for objeto in self.partida.objetos()}
        if self.foco not in ids:
            self.foco = None
        if self.sob_mouse not in ids:
            self.sob_mouse = None
        acao = self.partida.diretor.acao_atual
        self.caixa.mostrar(acao)
        if isinstance(acao, AbrirTela):
            self.menu.fechar()
            self.jogo.trocar_estado(TELAS[acao.tela](self))

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(Paleta.FUNDO)
        destacados = {self.foco, self.sob_mouse}
        mostrando = self.mostrando_objetos
        for objeto in self.partida.objetos():
            area = _retangulo(objeto)
            pygame.draw.rect(tela, Paleta.OBJETO, area)
            if mostrando:
                # Todos destacados; o foco e o mouse ganham a borda mais grossa.
                espessura = 2 if objeto.id in destacados else 1
                pygame.draw.rect(tela, Paleta.DESTAQUE, area, espessura)
            else:
                borda = Paleta.DESTAQUE if objeto.id in destacados else Paleta.APAGADO
                pygame.draw.rect(tela, borda, area, 1)
        if mostrando:
            self._desenhar_rotulos(tela)
        elif not self.partida.ocupada:
            self._desenhar_nome(tela)
        if not self.partida.ocupada:
            self._desenhar_botao(tela, self.botao_caderno, self._rotulo_caderno)
        if self.mapa_liberado:
            self._desenhar_botao(tela, self.botao_mapa, self._rotulo_mapa)
        self.menu.desenhar(tela)
        self.caixa.desenhar(tela)

    def _desenhar_botao(
        self, tela: pygame.Surface, botao: pygame.Rect, rotulo: pygame.Surface
    ) -> None:
        pygame.draw.rect(tela, Paleta.FUNDO, botao)
        pygame.draw.rect(tela, Paleta.TEXTO, botao, 1)
        tela.blit(rotulo, rotulo.get_rect(center=botao.center))

    def rotulos(self) -> list[tuple[Objeto, pygame.Rect]]:
        """Cada objeto visível com o retângulo onde o nome dele é escrito (Mostrar objetos)."""
        objetos = self.partida.objetos()
        tamanhos = [self._tamanho_rotulo(objeto) for objeto in objetos]
        botoes = [self.botao_caderno, *([self.botao_mapa] if self.mapa_liberado else [])]
        areas = [_retangulo(objeto) for objeto in objetos]
        postos = rotulos.posicionar(areas, tamanhos, self.jogo.tela.get_rect(), botoes)
        return list(zip(objetos, postos, strict=True))

    def _nome(self, objeto: Objeto) -> str:
        # ids-de-texto: dados (os nomes vêm do cenas.toml)
        return self.jogo.textos[objeto.nome].texto

    def _tamanho_rotulo(self, objeto: Objeto) -> tuple[int, int]:
        largura, altura = self.fonte.size(self._nome(objeto))
        return largura + 4, altura

    def _desenhar_rotulos(self, tela: pygame.Surface) -> None:
        destacados = {self.foco, self.sob_mouse}
        for objeto, posto in self.rotulos():
            cor = Paleta.DESTAQUE if objeto.id in destacados else Paleta.TEXTO
            nome = renderizar(self.fonte, self._nome(objeto), cor)
            pygame.draw.rect(tela, Paleta.FUNDO, posto)
            tela.blit(nome, nome.get_rect(center=posto.center))

    def _desenhar_nome(self, tela: pygame.Surface) -> None:
        """O nome do objeto sob o mouse (ou com o foco) numa faixa no alto da tela."""
        id_objeto = self.sob_mouse or self.foco
        objeto = next((obj for obj in self.partida.objetos() if obj.id == id_objeto), None)
        if objeto is None:
            return
        nome = renderizar(self.fonte, self._nome(objeto), Paleta.TEXTO)
        faixa = nome.get_rect(midtop=(LARGURA_TELA // 2, 2)).inflate(8, 2)
        pygame.draw.rect(tela, Paleta.FUNDO, faixa)
        tela.blit(nome, nome.get_rect(center=faixa.center))


def _retangulo(objeto: Objeto) -> pygame.Rect:
    return pygame.Rect(objeto.area.x, objeto.area.y, objeto.area.largura, objeto.area.altura)
