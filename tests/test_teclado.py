"""O jogo de ponta a ponta só com o teclado, na cena de teste real, com o driver `dummy` (I4).

Cada tecla passa pela tela atual como no loop do `Jogo`: o evento, depois `atualizar` e
`desenhar` na tela que estiver na frente (a tecla pode ter trocado de tela).
"""

import pygame

from politicalizando.dominio.acoes import Escolha, Fala
from politicalizando.estados.caderno import EstadoCaderno
from politicalizando.estados.cena import EstadoCena
from politicalizando.estados.comparacao import EstadoComparacao
from politicalizando.estados.mapa import EstadoMapa
from politicalizando.estados.materia import EstadoMateria
from politicalizando.estados.titulo import EstadoTitulo
from politicalizando.persistencia import carregar


def apertar(jogo, key, mod=0):
    jogo.estado.tratar_evento(pygame.Event(pygame.KEYDOWN, key=key, mod=mod))
    jogo.estado.atualizar(0)
    jogo.estado.desenhar(jogo.tela)


def cena(jogo) -> EstadoCena:
    assert isinstance(jogo.estado, EstadoCena)
    return jogo.estado


def confirmar_falas(jogo):
    """Enter até a caixa liberar a cena (falha numa escolha, que pede outra tecla)."""
    for _ in range(20):
        acao = cena(jogo).partida.diretor.acao_atual
        if acao is None and not cena(jogo).partida.ocupada:
            return
        assert isinstance(acao, Fala), f"esperava uma fala, veio {acao!r}"
        apertar(jogo, pygame.K_RETURN)
    raise AssertionError("a cena não liberou o input")


def focar(jogo, id_objeto):
    """Tab até o objeto ter o foco."""
    for _ in range(len(cena(jogo).partida.objetos())):
        apertar(jogo, pygame.K_TAB)
        if cena(jogo).foco == id_objeto:
            return
    raise AssertionError(f"o Tab não chegou em {id_objeto!r}")


def test_capitulo_de_teste_inteiro_pelo_teclado(jogo):
    jogo.trocar_estado(EstadoTitulo(jogo))

    # Novo jogo pela tecla 1, e as boas-vindas.
    apertar(jogo, pygame.K_1)
    assert cena(jogo).partida.cena.id == "teste.sala"
    confirmar_falas(jogo)

    # Mostrar objetos liga e desliga.
    apertar(jogo, pygame.K_o)
    assert cena(jogo).mostrando_objetos
    apertar(jogo, pygame.K_o)
    assert not cena(jogo).mostrando_objetos

    # Checar o mural: Olhar (1), a fala do post e a escolha "Opinião" com as setas.
    focar(jogo, "mural")
    apertar(jogo, pygame.K_1)
    apertar(jogo, pygame.K_RETURN)
    assert isinstance(cena(jogo).partida.diretor.acao_atual, Escolha)
    apertar(jogo, pygame.K_DOWN)
    apertar(jogo, pygame.K_RETURN)
    confirmar_falas(jogo)
    estado = cena(jogo).partida.estado
    assert estado.tem_flag("teste.mural.checou")
    assert estado.tem_flag("teste.mural.acertou")

    # O caderno abre e fecha com C e Esc.
    apertar(jogo, pygame.K_c)
    assert isinstance(jogo.estado, EstadoCaderno)
    apertar(jogo, pygame.K_ESCAPE)
    cena(jogo)

    # O mapa (M), já liberado pela checagem: → vai da sala ao corredor.
    apertar(jogo, pygame.K_m)
    assert isinstance(jogo.estado, EstadoMapa)
    apertar(jogo, pygame.K_RIGHT)
    apertar(jogo, pygame.K_RETURN)
    confirmar_falas(jogo)
    assert cena(jogo).partida.cena.id == "teste.corredor"

    # O quadro de propostas abre a comparação; o Esc fecha e o roteiro continua.
    focar(jogo, "quadro")
    apertar(jogo, pygame.K_2)
    assert isinstance(jogo.estado, EstadoComparacao)
    apertar(jogo, pygame.K_ESCAPE)
    assert cena(jogo).partida.diretor.acao_atual == Fala("teste.corredor.quadro.depois")
    confirmar_falas(jogo)

    # De volta à sala pela porta.
    focar(jogo, "porta")
    apertar(jogo, pygame.K_2)
    confirmar_falas(jogo)
    assert cena(jogo).partida.cena.id == "teste.sala"

    # A máquina de escrever abre a matéria: incluir a primeira peça, entregar (E), publicar (P).
    focar(jogo, "maquina")
    apertar(jogo, pygame.K_2)
    materia = jogo.estado
    assert isinstance(materia, EstadoMateria)
    apertar(jogo, pygame.K_RETURN)
    assert materia.inclusoes(), "o Enter incluiu a peça selecionada"
    apertar(jogo, pygame.K_e)
    assert materia.avaliacao is not None
    apertar(jogo, pygame.K_p)
    confirmar_falas(jogo)
    assert cena(jogo).partida.estado.tem_flag("materia.publicou")

    # Esc volta ao título salvando; a tecla 2 continua de onde parou.
    apertar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado, EstadoTitulo)
    assert carregar().tem_flag("materia.publicou")
    apertar(jogo, pygame.K_2)
    confirmar_falas(jogo)
    retomada = cena(jogo).partida
    assert retomada.cena.id == "teste.sala"
    assert retomada.estado.tem_flag("materia.publicou")
    assert retomada.estado.tem_flag("teste.mural.checou")
