"""Onde escrever o nome de cada objeto quando "Mostrar objetos" está ligado (I8).

Cada rótulo fica junto do seu objeto: acima, abaixo, dentro (se couber), à direita ou à
esquerda. Valem as posições que cabem na tela; só se nenhuma couber, o rótulo é empurrado para
dentro dela. Fica a primeira posição que não cobre outro rótulo nem outro objeto; se nenhuma
servir, a que cobre menos (cobrir um rótulo pesa mais que cobrir um objeto).
"""

from __future__ import annotations

from collections.abc import Sequence

import pygame

# Espaço entre o objeto e o rótulo.
FOLGA = 1
# Cobrir um rótulo esconde um nome; cobrir um objeto só esconde parte dele.
PESO_ROTULO = 10


def _candidatos(area: pygame.Rect, largura: int, altura: int) -> list[pygame.Rect]:
    rotulo = pygame.Rect(0, 0, largura, altura)
    acima = rotulo.copy()
    acima.midbottom = (area.centerx, area.top - FOLGA)
    abaixo = rotulo.copy()
    abaixo.midtop = (area.centerx, area.bottom + FOLGA)
    direita = rotulo.copy()
    direita.midleft = (area.right + FOLGA, area.centery)
    esquerda = rotulo.copy()
    esquerda.midright = (area.left - FOLGA, area.centery)
    candidatos = [acima, abaixo]
    if largura <= area.width and altura <= area.height:
        candidatos.append(rotulo.copy())
        candidatos[-1].center = area.center
    return [*candidatos, direita, esquerda]


def posicionar(
    areas: Sequence[pygame.Rect],
    tamanhos: Sequence[tuple[int, int]],
    limite: pygame.Rect,
    obstaculos: Sequence[pygame.Rect] = (),
) -> list[pygame.Rect]:
    """Um retângulo de rótulo para cada área, na mesma ordem.

    `tamanhos` traz a largura e a altura de cada rótulo; `limite` é a tela; `obstaculos` são
    outras coisas que os rótulos não devem cobrir (ex.: os botões no canto).
    """
    postos: list[pygame.Rect] = []
    for indice, (area, (largura, altura)) in enumerate(zip(areas, tamanhos, strict=True)):
        outros = [*obstaculos, *(a for i, a in enumerate(areas) if i != indice)]

        def custo(rotulo: pygame.Rect, outros: list[pygame.Rect] = outros) -> int:
            return PESO_ROTULO * len(rotulo.collidelistall(postos)) + len(
                rotulo.collidelistall(outros)
            )

        candidatos = _candidatos(area, largura, altura)
        cabem = [rotulo for rotulo in candidatos if limite.contains(rotulo)]
        candidatos = cabem or [rotulo.clamp(limite) for rotulo in candidatos]
        # `min` fica com o primeiro de menor custo: a ordem dos candidatos é a preferência.
        postos.append(min(candidatos, key=custo))
    return postos
