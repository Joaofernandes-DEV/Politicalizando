"""Configuração dos testes: pygame sem janela nem áudio (funciona no CI)."""

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402 - precisa vir depois das variáveis de ambiente

from politicalizando.jogo import Jogo  # noqa: E402


@pytest.fixture
def jogo():
    """Instância do jogo com janela virtual; o pygame é encerrado no fim do teste."""
    instancia = Jogo()
    yield instancia
    pygame.quit()
