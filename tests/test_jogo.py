import pygame

from politicalizando.__main__ import main
from politicalizando.config import ALTURA_TELA, LARGURA_TELA
from politicalizando.estados.titulo import EstadoTitulo


def test_janela_usa_a_resolucao_logica(jogo):
    assert jogo.tela.get_size() == (LARGURA_TELA, ALTURA_TELA)


def test_esc_na_tela_de_titulo_encerra_sem_erro(jogo):
    jogo.trocar_estado(EstadoTitulo(jogo))
    pygame.event.post(pygame.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    jogo.executar()
    assert not jogo.rodando
    assert not pygame.get_init()


def test_fechar_em_abre_e_fecha_sozinho():
    main(["--fechar-em", "0.2"])
    assert not pygame.get_init()
