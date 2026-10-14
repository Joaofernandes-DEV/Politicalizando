"""Constantes do jogo: janela, ritmo e cores."""

TITULO = "Politicalizando"

# Resolução lógica da pixel art (16:9). O pygame.SCALED amplia a janela por um fator
# inteiro, sem borrar os pixels.
LARGURA_TELA = 320
ALTURA_TELA = 180

FPS = 60

Cor = tuple[int, int, int]


class Paleta:
    """Cores provisórias da Fase 0; a paleta final é definida na Fase 3 (I1)."""

    FUNDO: Cor = (18, 16, 28)
    TEXTO: Cor = (226, 226, 214)
    DESTAQUE: Cor = (214, 72, 96)
    APAGADO: Cor = (110, 108, 124)
    # Preenchimento dos retângulos que fazem as vezes da arte na Fase 2.
    OBJETO: Cor = (44, 42, 64)
