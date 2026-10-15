"""Partida em andamento: o estado, o diretor e a interação com as cenas juntos (D10, D11).

A tela de cena só desenha e lê o input; as regras de quando o jogador pode agir, de quando a
entrada de uma cena roda e de quando é hora do autosave ficam aqui, testadas sem janela:

- enquanto o diretor está ocupado (ou a cena nova ainda não foi preparada), a partida está
  `ocupada` e recusa verbos: o input fica bloqueado;
- quando a cena atual muda e o diretor está livre, a partida roda `ao_entrar` da cena nova. Uma
  `TrocarCena` no meio de um roteiro troca a cena na hora, mas a entrada só roda depois que o
  roteiro termina;
- `atualizar` devolve `True` quando a entrada numa cena terminou: é a hora do autosave
  (`autosalvar(partida.estado, bloqueado=partida.ocupada)`), já com a visita e os efeitos da
  entrada, para que ela não se repita ao continuar o jogo.
"""

from __future__ import annotations

from politicalizando.dominio.acoes import Fala, Roteiro, TrocarCena
from politicalizando.dominio.cenas import Cena, Objeto, Verbo
from politicalizando.dominio.diretor import Diretor
from politicalizando.dominio.estado_jogo import EstadoJogo, SaveInvalido
from politicalizando.dominio.interacao import Interacao, objeto_em, objetos_visiveis


class Partida:
    def __init__(self, estado: EstadoJogo, interacao: Interacao) -> None:
        """Levanta `SaveInvalido` se a cena do estado não existe (ex.: save de outra versão)."""
        if estado.cena_atual not in interacao.cenas:
            raise SaveInvalido(f"a cena do save não existe: {estado.cena_atual!r}")
        self.estado = estado
        self.interacao = interacao
        self.diretor = Diretor(estado)
        # A cena cuja entrada já rodou; `None` faz a primeira cena ser preparada.
        self._cena_preparada: str | None = None
        self._entrando = False

    @classmethod
    def nova(cls, interacao: Interacao) -> Partida:
        """Um jogo novo, na cena `inicio` do `cenas.toml`."""
        inicio = interacao.cenas.inicio
        if inicio is None:
            raise ValueError("as cenas não definem onde o jogo começa ('inicio')")
        estado = EstadoJogo()
        estado.entrar_na_cena(inicio)
        return cls(estado, interacao)

    @property
    def ocupada(self) -> bool:
        """Há uma sequência rodando ou uma cena nova por preparar: input e autosave bloqueados."""
        return self.diretor.ocupado or self.estado.cena_atual != self._cena_preparada

    @property
    def cena(self) -> Cena:
        """A cena atual, que é a que aparece na tela (muda na hora de uma `TrocarCena`)."""
        return self.interacao.cenas[self.estado.cena_atual]

    def objetos(self) -> tuple[Objeto, ...]:
        """Os objetos visíveis da cena atual, na ordem de percorrer com o teclado."""
        return objetos_visiveis(self.cena, self.estado)

    def objeto_em(self, x: float, y: float) -> Objeto | None:
        return objeto_em(self.cena, self.estado, x, y)

    def agir(self, objeto: Objeto, verbo: Verbo | str) -> bool:
        """Começa a resposta do objeto ao verbo; devolve `False` se a partida está ocupada."""
        if self.ocupada:
            return False
        self.diretor.iniciar(self.interacao.agir(self.estado, objeto, verbo))
        return True

    def ir_para(self, id_cena: str) -> bool:
        """Vai para outra cena pelo mapa; a entrada e o autosave seguem o caminho de sempre.

        Devolve `False` se a partida está ocupada ou se já está nessa cena.
        """
        if id_cena not in self.interacao.cenas:
            raise KeyError(f"cena inexistente: {id_cena!r}")
        if self.ocupada or id_cena == self.estado.cena_atual:
            return False
        self.diretor.iniciar(_trocar_cena(id_cena))
        return True

    def avisar(self, fala: Fala) -> None:
        """Mostra um aviso do jogo (ex.: o save falhou) na caixa, como uma fala.

        Recebe a `Fala` pronta (`Fala("id")`) para o teste de textos usados achar o ID.
        """
        self.diretor.iniciar(_aviso(fala))

    def confirmar(self) -> bool:
        return self.diretor.confirmar()

    def concluir_tela(self) -> bool:
        return self.diretor.concluir_tela()

    def escolher(self, indice: int) -> bool:
        return self.diretor.escolher(indice)

    def atualizar(self, dt: float) -> bool:
        """Avança o tempo e prepara a cena nova; `True` quando a entrada numa cena terminou."""
        self.diretor.atualizar(dt)
        while not self.diretor.ocupado:
            if self.estado.cena_atual != self._cena_preparada:
                # A entrada pode trocar de cena de novo; o laço prepara a seguinte.
                self._cena_preparada = self.estado.cena_atual
                self._entrando = True
                self.diretor.iniciar(self.interacao.ao_entrar(self.estado, self._cena_preparada))
            elif self._entrando:
                self._entrando = False
                return True
            else:
                return False
        return False


def _aviso(fala: Fala) -> Roteiro:
    yield fala


def _trocar_cena(id_cena: str) -> Roteiro:
    yield TrocarCena(id_cena)
