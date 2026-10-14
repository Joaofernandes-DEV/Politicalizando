"""Interação com as cenas: objetos visíveis, clique, verbos e entrada (D8, J9, J10, I4).

Tudo devolve roteiros para o `Diretor`; nada aqui desenha ou lê o mouse. O jogo chama
`ao_entrar` quando a cena muda e o diretor está livre, para não iniciar uma sequência por cima
de outra.
"""

from __future__ import annotations

from collections.abc import Mapping

from politicalizando.dominio.acoes import Acao, Fala, MarcarFlag, Roteiro
from politicalizando.dominio.cenas import Cena, Cenas, Objeto, Resposta, Verbo, conferir_referencias
from politicalizando.dominio.dialogo import Dialogo
from politicalizando.dominio.estado_jogo import EstadoJogo
from politicalizando.dominio.roteiro import Sequencia


def objetos_visiveis(cena: Cena, estado: EstadoJogo) -> tuple[Objeto, ...]:
    """Na ordem do arquivo, que também é a ordem de percorrer com o teclado (I4)."""
    return tuple(objeto for objeto in cena.objetos if objeto.visivel(estado))


def objeto_em(cena: Cena, estado: EstadoJogo, x: float, y: float) -> Objeto | None:
    """O objeto visível sob o ponto; se houver sobreposição, o último da lista fica por cima."""
    for objeto in reversed(objetos_visiveis(cena, estado)):
        if objeto.area.contem(x, y):
            return objeto
    return None


def _passos(acoes: tuple[Acao, ...]) -> Roteiro:
    yield from acoes


class Interacao:
    """Resolve verbos e entradas em roteiros. As recusas genéricas alternam por verbo."""

    def __init__(
        self,
        cenas: Cenas,
        roteiros: Mapping[str, Sequencia],
        dialogos: Mapping[str, Dialogo],
    ) -> None:
        conferir_referencias(cenas, roteiros, dialogos)
        self.cenas = cenas
        self.roteiros = roteiros
        self.dialogos = dialogos
        # Rodízio determinístico, sem sorteio; é só variação de texto e não vai no save.
        self._proxima_recusa = dict.fromkeys(Verbo, 0)

    def agir(self, estado: EstadoJogo, objeto: Objeto, verbo: Verbo | str) -> Roteiro:
        """A resposta do objeto ao verbo, ou a próxima recusa genérica daquele verbo."""
        verbo = Verbo(verbo)
        resposta = objeto.respostas.get(verbo)
        if resposta is not None:
            return self._executar(resposta, estado)
        recusas = self.cenas.recusas[verbo]
        indice = self._proxima_recusa[verbo]
        self._proxima_recusa[verbo] = (indice + 1) % len(recusas)
        # ids-de-texto: dados (as recusas vêm do cenas.toml)
        return _passos((Fala(recusas[indice]),))

    def ao_entrar(self, estado: EstadoJogo, id_cena: str) -> Roteiro:
        """Marca `<cena>.visitou` e, só na primeira visita, roda a `entrada` da cena (J10)."""
        cena = self.cenas[id_cena]
        primeira_visita = not estado.tem_flag(cena.flag_visitou)

        def roteiro() -> Roteiro:
            yield MarcarFlag(cena.flag_visitou)
            if primeira_visita and cena.entrada is not None:
                yield from self._executar(cena.entrada, estado)

        return roteiro()

    def _executar(self, resposta: Resposta, estado: EstadoJogo) -> Roteiro:
        if resposta.roteiro is not None:
            return self.roteiros[resposta.roteiro].executar(estado)
        if resposta.dialogo is not None:
            return self.dialogos[resposta.dialogo].executar(estado)
        return _passos(resposta.passos)
