"""Configuração dos testes: pygame sem janela nem áudio (funciona no CI) e pasta de dados
temporária, para nenhum teste tocar no save real."""

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402 - precisa vir depois das variáveis de ambiente

from politicalizando.jogo import Jogo  # noqa: E402
from politicalizando.persistencia import VARIAVEL_DADOS  # noqa: E402


@pytest.fixture(autouse=True)
def pasta_dados(tmp_path, monkeypatch):
    """Aponta a pasta de dados do jogo para uma pasta temporária em todos os testes."""
    pasta = tmp_path / "dados"
    monkeypatch.setenv(VARIAVEL_DADOS, str(pasta))
    return pasta


@pytest.fixture
def jogo():
    """Instância do jogo com janela virtual; o pygame é encerrado no fim do teste."""
    instancia = Jogo()
    yield instancia
    pygame.quit()
