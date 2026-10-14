"""Toda flag citada numa condição (`se`, `se_nao`) é marcada em algum lugar dos dados.

Pega erros de digitação: uma condição com uma flag que nunca é marcada esconderia (ou mostraria)
uma opção para sempre. Hoje as flags vêm dos roteiros e dos diálogos em dados. Quando surgir um
roteiro especial em Python que marque flags, a varredura de código de `test_textos_usados.py`
passa a coletar também `MarcarFlag("...")`.
"""

from politicalizando.conteudo import carregar_dialogos, carregar_roteiros
from politicalizando.dominio.acoes import MarcarFlag
from politicalizando.dominio.dialogo import Dialogos
from politicalizando.dominio.roteiro import Roteiros


def flags_marcadas(roteiros: Roteiros, dialogos: Dialogos) -> set[str]:
    dos_roteiros = {
        acao.flag
        for sequencia in roteiros.values()
        for acao in sequencia.acoes
        if isinstance(acao, MarcarFlag)
    }
    return dos_roteiros | dialogos.flags_marcadas()


def flags_sem_origem(roteiros: Roteiros, dialogos: Dialogos) -> list[str]:
    return sorted(dialogos.flags_exigidas() - flags_marcadas(roteiros, dialogos))


def test_flag_exigida_marcada_por_um_roteiro_ou_dialogo_passa():
    roteiros = Roteiros.de_toml('exemplo.entrada = [{ marcar_flag = "exemplo.visitou" }]')
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\nopcoes = ['
        '{ id = "x", texto = "exemplo.x", vai_para = "fim", se = ["exemplo.visitou"] },'
        '{ id = "y", texto = "exemplo.y", vai_para = "fim", se_nao = ["exemplo.guia.x"] }]'
    )
    assert flags_sem_origem(roteiros, dialogos) == []


def test_flag_exigida_que_ninguem_marca_e_acusada():
    dialogos = Dialogos.de_toml(
        '[exemplo.guia]\ninicio = "a"\n[exemplo.guia.nos.a]\nopcoes = ['
        '{ id = "x", texto = "exemplo.x", vai_para = "fim", se = ["exemplo.visituo"] }]'
    )
    assert flags_sem_origem(Roteiros(), dialogos) == ["exemplo.visituo"]


def test_toda_flag_exigida_nos_dados_do_jogo_e_marcada():
    assert flags_sem_origem(carregar_roteiros(), carregar_dialogos()) == []
