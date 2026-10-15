"""Onde os nomes dos objetos ficam com "Mostrar objetos" ligado (I8)."""

import pygame

from politicalizando.ui.rotulos import posicionar

TELA = pygame.Rect(0, 0, 320, 180)


def test_o_rotulo_fica_logo_acima_do_objeto():
    (rotulo,) = posicionar([pygame.Rect(100, 50, 40, 40)], [(30, 12)], TELA)
    assert rotulo.size == (30, 12)
    assert rotulo.bottom == 49
    assert rotulo.centerx == 120


def test_sem_espaco_acima_o_rotulo_vai_para_baixo():
    (rotulo,) = posicionar([pygame.Rect(100, 2, 40, 40)], [(30, 12)], TELA)
    assert rotulo.top == 43


def test_o_rotulo_nunca_sai_da_tela():
    areas = [pygame.Rect(0, 0, 10, 180), pygame.Rect(312, 0, 8, 8)]
    for rotulo in posicionar(areas, [(60, 12), (60, 12)], TELA):
        assert TELA.contains(rotulo)


def test_rotulos_vizinhos_nao_se_cobrem():
    # Dois objetos lado a lado: os rótulos acima colidiriam, então o segundo muda de lugar.
    areas = [pygame.Rect(100, 60, 20, 20), pygame.Rect(122, 60, 20, 20)]
    primeiro, segundo = posicionar(areas, [(40, 12), (40, 12)], TELA)
    assert not primeiro.colliderect(segundo)


def test_o_rotulo_evita_cobrir_outro_objeto():
    # Um objeto pequeno logo acima do grande: o nome do grande não cobre o pequeno.
    grande = pygame.Rect(110, 100, 70, 26)
    pequeno = pygame.Rect(134, 92, 18, 10)
    rotulo_grande, rotulo_pequeno = posicionar([grande, pequeno], [(30, 12), (34, 12)], TELA)
    assert not rotulo_grande.colliderect(pequeno)
    assert not rotulo_pequeno.colliderect(rotulo_grande)


def test_o_rotulo_evita_os_obstaculos():
    botao = pygame.Rect(90, 30, 60, 14)
    (rotulo,) = posicionar([pygame.Rect(100, 50, 40, 40)], [(30, 12)], TELA, [botao])
    assert not rotulo.colliderect(botao)
