import tomllib
from pathlib import Path

import politicalizando

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_versao_do_pacote_igual_a_do_pyproject():
    with PYPROJECT.open("rb") as arquivo:
        versao_pyproject = tomllib.load(arquivo)["project"]["version"]
    assert politicalizando.__version__ == versao_pyproject
