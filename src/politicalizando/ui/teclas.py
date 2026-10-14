"""Teclas comuns a todas as telas (I4): confirmar, voltar, navegar e números."""

import pygame

CONFIRMAR = frozenset({pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE})
ANTERIOR = frozenset({pygame.K_UP, pygame.K_LEFT})
PROXIMO = frozenset({pygame.K_DOWN, pygame.K_RIGHT})

_NUMEROS = {
    **{getattr(pygame, f"K_{n}"): n - 1 for n in range(1, 10)},
    **{getattr(pygame, f"K_KP{n}"): n - 1 for n in range(1, 10)},
}


def numero(tecla: int) -> int | None:
    """O índice (a partir de 0) das teclas 1 a 9, da linha de cima ou do teclado numérico."""
    return _NUMEROS.get(tecla)


def clique_esquerdo(evento: pygame.Event) -> bool:
    return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
