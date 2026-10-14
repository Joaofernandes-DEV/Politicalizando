import subprocess
import sys

# Roda num processo novo: nos testes o pygame já está carregado pelo conftest.
VERIFICACAO = """
import importlib, pkgutil, sys
import politicalizando.dominio as dominio
for modulo in pkgutil.walk_packages(dominio.__path__, dominio.__name__ + "."):
    importlib.import_module(modulo.name)
print("pygame" in sys.modules)
"""


def test_dominio_nao_importa_pygame():
    resultado = subprocess.run(
        [sys.executable, "-c", VERIFICACAO], capture_output=True, text=True, check=True
    )
    assert resultado.stdout.strip() == "False"
