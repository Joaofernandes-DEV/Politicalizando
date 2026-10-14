import json
from pathlib import Path

import pytest

from politicalizando import persistencia
from politicalizando.dominio.estado_jogo import EstadoJogo, SaveInvalido
from politicalizando.persistencia import (
    autosalvar,
    caminho_save,
    carregar,
    existe_save,
    salvar,
)

RAIZ_DO_PROJETO = Path(__file__).resolve().parents[1]


def estado_com_progresso() -> EstadoJogo:
    estado = EstadoJogo()
    estado.entrar_na_cena("praca")
    estado.marcar_flag("praca.visitou")
    estado.dar_item("panfleto_do_feed")
    return estado


def test_save_fica_na_pasta_temporaria_dos_testes(pasta_dados):
    assert caminho_save() == pasta_dados / "save.json"


def test_sem_a_variavel_o_save_fica_em_dados_ao_lado_do_jogo(monkeypatch):
    monkeypatch.delenv(persistencia.VARIAVEL_DADOS)
    assert caminho_save() == RAIZ_DO_PROJETO / "dados" / "save.json"


def test_executavel_guarda_o_save_ao_lado_do_exe(monkeypatch, tmp_path):
    monkeypatch.delenv(persistencia.VARIAVEL_DADOS)
    monkeypatch.setattr(persistencia.sys, "frozen", True, raising=False)
    monkeypatch.setattr(persistencia.sys, "executable", str(tmp_path / "Politicalizando.exe"))
    assert caminho_save() == tmp_path.resolve() / "dados" / "save.json"


def test_sem_save_carregar_devolve_none():
    assert not existe_save()
    assert carregar() is None


def test_salvar_e_carregar(pasta_dados):
    salvar(estado_com_progresso())
    assert existe_save()

    carregado = carregar()
    assert carregado.cena_atual == "praca"
    assert carregado.flags == {"praca.visitou"}
    assert carregado.inventario == ("panfleto_do_feed",)
    assert not carregado.alterado


def test_arquivo_gravado_segue_o_formato_documentado():
    salvar(estado_com_progresso())
    assert json.loads(caminho_save().read_text(encoding="utf-8")) == {
        "versao": 1,
        "cena_atual": "praca",
        "flags": ["praca.visitou"],
        "inventario": ["panfleto_do_feed"],
    }


def test_salvar_cria_a_pasta_e_marca_como_salvo(pasta_dados):
    assert not pasta_dados.exists()
    estado = estado_com_progresso()
    salvar(estado)
    assert pasta_dados.is_dir()
    assert not estado.alterado


def test_salvar_sobrescreve_e_nao_deixa_temporario(pasta_dados):
    estado = estado_com_progresso()
    salvar(estado)
    estado.entrar_na_cena("biblioteca")
    salvar(estado)
    assert carregar().cena_atual == "biblioteca"
    assert sorted(p.name for p in pasta_dados.iterdir()) == ["save.json"]


@pytest.mark.parametrize(
    "conteudo",
    [
        pytest.param(b"{ isto nao e json", id="json-quebrado"),
        pytest.param(b"\xff\xfe\x00", id="bytes-invalidos"),
        pytest.param(
            b'{"versao": 99, "cena_atual": null, "flags": [], "inventario": []}',
            id="versao-futura",
        ),
    ],
)
def test_save_ilegivel_levanta_erro_e_nao_e_apagado(pasta_dados, conteudo):
    pasta_dados.mkdir()
    caminho_save().write_bytes(conteudo)
    with pytest.raises(SaveInvalido):
        carregar()
    assert caminho_save().read_bytes() == conteudo


def test_autosalvar_grava_quando_houve_mudanca():
    estado = estado_com_progresso()
    assert autosalvar(estado, bloqueado=False)
    assert existe_save()
    assert not estado.alterado


def test_autosalvar_nao_grava_quando_bloqueado():
    estado = estado_com_progresso()
    assert not autosalvar(estado, bloqueado=True)
    assert not existe_save()
    assert estado.alterado


def test_autosalvar_nao_grava_sem_mudanca():
    estado = estado_com_progresso()
    salvar(estado)
    caminho_save().write_text("marcador", encoding="utf-8")
    estado.entrar_na_cena("praca")
    assert not autosalvar(estado, bloqueado=False)
    assert caminho_save().read_text(encoding="utf-8") == "marcador"


def test_entrar_numa_cena_nova_dispara_o_autosave():
    # D10: depois de salvar, entrar num local novo grava o progresso com a nova cena.
    estado = estado_com_progresso()
    salvar(estado)
    estado.entrar_na_cena("biblioteca")
    estado.marcar_flag("biblioteca.visitou")
    assert autosalvar(estado, bloqueado=False)

    carregado = carregar()
    assert carregado.cena_atual == "biblioteca"
    assert carregado.tem_flag("biblioteca.visitou")
