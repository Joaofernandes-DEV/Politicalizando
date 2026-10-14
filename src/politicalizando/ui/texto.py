"""Texto na tela: a fonte provisória e a quebra de linhas na largura disponível."""

import pygame

from politicalizando.config import Cor

# Fonte padrão do pygame até a fonte pixel com acentos chegar (Fase 3, I2).
TAMANHO_FONTE = 16


def criar_fonte() -> pygame.font.Font:
    return pygame.font.Font(None, TAMANHO_FONTE)


def renderizar(fonte: pygame.font.Font, texto: str, cor: Cor) -> pygame.Surface:
    # Sem antialiasing: o texto fica com o mesmo pixel duro da arte.
    return fonte.render(texto, False, cor)


def quebrar_linhas(fonte: pygame.font.Font, texto: str, largura: int) -> list[str]:
    """Quebra o texto em linhas que cabem na largura, sem cortar palavras.

    Uma palavra maior que a largura fica sozinha na linha (e passa da borda); o teste de que
    todo texto cabe na caixa acusa esse caso.
    """
    linhas: list[str] = []
    for paragrafo in texto.split("\n"):
        atual = ""
        for palavra in paragrafo.split():
            candidata = f"{atual} {palavra}" if atual else palavra
            if atual and fonte.size(candidata)[0] > largura:
                linhas.append(atual)
                atual = palavra
            else:
                atual = candidata
        linhas.append(atual)
    return linhas
