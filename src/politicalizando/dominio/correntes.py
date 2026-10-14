"""As 4 correntes da V1 (briefing, seção 5), como IDs para marcar os dados.

A marcação serve para conferir o equilíbrio por teste (E3, E5): mesma estrutura de diálogo e
mesma distribuição de exemplos para cada corrente. Ela nunca vira flag nem pontuação (E1).
"""

CORRENTES = ("liberalismo", "conservadorismo", "socialismo", "social_democracia")


def validar_corrente(corrente: object) -> str:
    """Devolve a corrente se ela for uma das 4; senão levanta `ValueError`."""
    if corrente not in CORRENTES:
        raise ValueError(f"corrente desconhecida: {corrente!r} (aceitas: {', '.join(CORRENTES)})")
    return corrente
