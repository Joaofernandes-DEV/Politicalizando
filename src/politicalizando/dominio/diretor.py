"""Diretor: executa os roteiros uma ação por vez (D11, briefing seção 3).

As ações instantâneas (`MarcarFlag`, `DarItem`, `TrocarCena`) são aplicadas no estado na hora,
para que o roteiro já veja o resultado na linha seguinte. Nas ações de espera, o diretor para e
aguarda: `confirmar()` encerra uma `Fala`, `escolher()` responde uma `Escolha` e `atualizar()`
desconta o tempo de um `Esperar`. Enquanto há sequência rodando, `ocupado` é `True`: o jogo
bloqueia o input e o autosave (`autosalvar(estado, bloqueado=diretor.ocupado)`).
"""

from __future__ import annotations

from collections.abc import Generator

from politicalizando.dominio.acoes import (
    AcaoDeEspera,
    DarItem,
    Escolha,
    Esperar,
    Fala,
    MarcarFlag,
    Roteiro,
    TrocarCena,
)
from politicalizando.dominio.estado_jogo import EstadoJogo


class Diretor:
    def __init__(self, estado: EstadoJogo) -> None:
        self.estado = estado
        self._roteiro: Roteiro | None = None
        self._acao: AcaoDeEspera | None = None
        self._restante = 0.0

    @property
    def ocupado(self) -> bool:
        """Há uma sequência rodando (o input e o autosave ficam bloqueados)."""
        return self._roteiro is not None

    @property
    def acao_atual(self) -> AcaoDeEspera | None:
        """A `Fala`, a `Escolha` ou o `Esperar` que está aguardando; `None` se nenhuma."""
        return self._acao

    def iniciar(self, roteiro: Roteiro) -> None:
        """Começa a sequência e corre até a primeira ação de espera (ou até o fim)."""
        if not isinstance(roteiro, Generator):
            raise TypeError(f"o roteiro precisa ser um gerador: {roteiro!r}")
        if self.ocupado:
            raise RuntimeError("já há uma sequência rodando")
        self._roteiro = roteiro
        self._avancar(None)

    def confirmar(self) -> bool:
        """Encerra a `Fala` atual (tecla ou clique); devolve `False` se não há fala esperando."""
        if not isinstance(self._acao, Fala):
            return False
        self._avancar(None)
        return True

    def escolher(self, indice: int) -> bool:
        """Responde a `Escolha` atual; devolve `False` se não há escolha esperando.

        Um índice fora das opções levanta `ValueError`, e a escolha continua esperando.
        """
        if not isinstance(self._acao, Escolha):
            return False
        quantidade = len(self._acao.opcoes)
        if isinstance(indice, bool) or not isinstance(indice, int) or not 0 <= indice < quantidade:
            raise ValueError(f"opção inválida: {indice!r} (há {quantidade})")
        self._avancar(indice)
        return True

    def atualizar(self, dt: float) -> None:
        """Desconta `dt` segundos do `Esperar` atual e segue quando o tempo acaba."""
        if not isinstance(self._acao, Esperar):
            return
        self._restante -= dt
        if self._restante <= 0:
            self._avancar(None)

    def _avancar(self, resposta: int | None) -> None:
        self._acao = None
        try:
            while True:
                try:
                    acao = self._roteiro.send(resposta)
                except StopIteration:
                    self._roteiro = None
                    return
                resposta = None
                if self._aplicar(acao):
                    return
        except Exception:
            # Um roteiro com defeito não deixa o diretor travado em "ocupado".
            self._descartar()
            raise

    def _aplicar(self, acao: object) -> bool:
        """Executa a ação; devolve `True` se ela espera o jogador ou o tempo."""
        match acao:
            case MarcarFlag(flag=flag):
                self.estado.marcar_flag(flag)
            case DarItem(item=item):
                self.estado.dar_item(item)
            case TrocarCena(cena=cena):
                self.estado.entrar_na_cena(cena)
            case Esperar(segundos=segundos):
                self._acao, self._restante = acao, segundos
                return True
            case Fala() | Escolha():
                self._acao = acao
                return True
            case _:
                raise TypeError(f"o roteiro produziu algo que não é uma ação: {acao!r}")
        return False

    def _descartar(self) -> None:
        if self._roteiro is not None:
            self._roteiro.close()
        self._roteiro = None
        self._acao = None
