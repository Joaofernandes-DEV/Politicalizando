"""Salvaguardas de equilíbrio nas mecânicas e no conteúdo (briefing, seções 5 e 6.1).

Aqui ficam o E3 (mesma estrutura de diálogo por corrente), o E4 (recusas sem correntes), o E5
(manipulação distribuída por igual) e o equilíbrio das fichas (mesmo modelo, tamanho parecido,
as 4 correntes). O E2 chega com a avaliação da matéria, no PR `feat/avaliacao-da-materia`.
"""

from collections import Counter

import pytest

from politicalizando.conteudo import (
    carregar_cenas,
    carregar_checagem,
    carregar_dialogos,
    carregar_fichas,
    carregar_textos,
)
from politicalizando.dominio.checagem import SEM_LADO, Casos, Classe
from politicalizando.dominio.correntes import CORRENTES
from politicalizando.dominio.dialogo import FIM, Dialogo, Dialogos
from politicalizando.dominio.fichas import Fichas
from politicalizando.dominio.textos import Textos

# A ficha mais longa pode ter no máximo 1,3× os caracteres da mais curta.
LIMITE_DE_TAMANHO_DAS_FICHAS = 1.3

# Trechos que indicam uma corrente no texto (sem acento e em minúsculas, para comparar).
TERMOS_DE_CORRENTE = ("liberal", "conservador", "socialis", "social-democra", "socialdemocra")


def _normalizar(texto: str) -> str:
    return texto.lower().translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))


def recusas_que_citam_correntes(recusas: set[str], textos: Textos) -> list[str]:
    return sorted(
        id_texto
        for id_texto in recusas
        if any(termo in _normalizar(textos[id_texto].texto) for termo in TERMOS_DE_CORRENTE)
    )


@pytest.mark.parametrize(
    "frase",
    [
        "Uma ideia bem liberal.",
        "Isso é coisa de Conservador.",
        "Parece socialismo.",
        "Bem social-democrata.",
        "Socialdemocracia pura.",
    ],
)
def test_e4_recusa_que_cita_uma_corrente_e_acusada(frase):
    textos = Textos.de_toml(f'[exemplo.recusa]\ntexto = "{frase}"')
    assert recusas_que_citam_correntes({"exemplo.recusa"}, textos) == ["exemplo.recusa"]


def test_e4_recusa_neutra_passa():
    textos = Textos.de_toml('[exemplo.recusa]\ntexto = "Não há nada de especial aqui."')
    assert recusas_que_citam_correntes({"exemplo.recusa"}, textos) == []


def test_e4_recusas_do_jogo_nunca_falam_de_correntes():
    recusas = set().union(*carregar_cenas().recusas.values())
    assert recusas_que_citam_correntes(recusas, carregar_textos()) == []


# --- Fichas: tamanho parecido e as 4 correntes ----------------------------------------------


def tamanhos_das_fichas(fichas: Fichas, textos: Textos) -> dict[str, int]:
    """Caracteres de todos os textos de cada ficha."""
    return {
        corrente: sum(len(textos[id_texto].texto) for id_texto in ficha.ids_de_texto())
        for corrente, ficha in fichas.items()
    }


def desequilibrio_das_fichas(fichas: Fichas, textos: Textos) -> str | None:
    """Uma mensagem se a ficha mais longa passa do limite em relação à mais curta."""
    tamanhos = tamanhos_das_fichas(fichas, textos)
    if len(tamanhos) < 2:
        return None
    maior = max(tamanhos, key=tamanhos.get)
    menor = min(tamanhos, key=tamanhos.get)
    if tamanhos[maior] > LIMITE_DE_TAMANHO_DAS_FICHAS * tamanhos[menor]:
        limite = f"{LIMITE_DE_TAMANHO_DAS_FICHAS:g}×".replace(".", ",")
        return (
            f"{maior} ({tamanhos[maior]}) passa de {limite} {menor} ({tamanhos[menor]}): {tamanhos}"
        )
    return None


# Ficha fictícia: a ideia central varia de tamanho; todos os outros itens usam o mesmo texto
# curto "exemplo.{c}.x".
_FICHA = """
[fichas.{c}]
ideia_central = "exemplo.{c}.ideia"
valores = ["exemplo.{c}.x"]
estado = "exemplo.{c}.x"
mercado = "exemplo.{c}.x"
sociedade = "exemplo.{c}.x"
origem = "exemplo.{c}.x"
pensadores = ["exemplo.{c}.x"]
proposta = "exemplo.{c}.x"
confusoes = ["exemplo.{c}.x"]
criticas = [{{ texto = "exemplo.{c}.x", de = "outras" }}, {{ texto = "exemplo.{c}.y", de = "{o}" }}]
fontes = [{{ autor = "Exemplo, Autor", titulo = "Obra", ano = 2000, editora = "Ed." }}]
"""


def _fichas_e_textos(tamanhos: dict[str, int]) -> tuple[Fichas, Textos]:
    fichas, textos = [], []
    for corrente, tamanho in tamanhos.items():
        outra = next(c for c in CORRENTES if c != corrente)
        fichas.append(_FICHA.format(c=corrente, o=outra))
        textos.append(
            f'[exemplo.{corrente}.ideia]\ntexto = "{"a" * tamanho}"\n'
            f'[exemplo.{corrente}.x]\ntexto = "b"\n'
            f'[exemplo.{corrente}.y]\ntexto = "c"\n'
        )
    return Fichas.de_toml("".join(fichas)), Textos.de_toml("".join(textos))


def test_fichas_de_tamanho_parecido_passam():
    fichas, textos = _fichas_e_textos({"liberalismo": 100, "socialismo": 120})
    assert desequilibrio_das_fichas(fichas, textos) is None


def test_ficha_muito_mais_longa_e_acusada():
    fichas, textos = _fichas_e_textos({"liberalismo": 100, "socialismo": 200})
    mensagem = desequilibrio_das_fichas(fichas, textos)
    assert mensagem is not None
    assert mensagem.startswith("socialismo")


def test_fichas_do_jogo_tem_tamanho_parecido():
    assert desequilibrio_das_fichas(carregar_fichas(), carregar_textos()) is None


@pytest.mark.xfail(
    strict=True,
    reason="As fichas reais entram na Fase 4. Quando as 4 chegarem, este teste passa e o "
    "xfail estrito acusa: remova a marcação para o teste virar obrigatório.",
)
def test_ha_uma_ficha_para_cada_uma_das_4_correntes():
    assert list(carregar_fichas()) == list(CORRENTES)


# --- E3: mesma estrutura de diálogo para cada corrente --------------------------------------


def perfil(dialogo: Dialogo) -> tuple[tuple[int, ...], ...]:
    """Tópicos e níveis: para cada nível a partir do início, o número de opções de cada nó."""
    profundidade = {dialogo.inicio: 0}
    fila = [dialogo.inicio]
    while fila:
        no = dialogo.nos[fila.pop(0)]
        destinos = [no.vai_para] if no.vai_para is not None else []
        destinos += [opcao.vai_para for opcao in no.opcoes]
        for destino in destinos:
            if destino != FIM and destino not in profundidade:
                profundidade[destino] = profundidade[no.id] + 1
                fila.append(destino)
    niveis = max(profundidade.values()) + 1
    return tuple(
        tuple(
            sorted(len(dialogo.nos[nome].opcoes) for nome, p in profundidade.items() if p == nivel)
        )
        for nivel in range(niveis)
    )


def desequilibrio_dos_dialogos(dialogos: Dialogos) -> str | None:
    """Uma mensagem se as correntes não têm o mesmo conjunto de perfis de diálogo."""
    por_corrente = {
        corrente: sorted(perfil(d) for d in dialogos.values() if d.corrente == corrente)
        for corrente in CORRENTES
    }
    referencia = por_corrente[CORRENTES[0]]
    if all(perfis == referencia for perfis in por_corrente.values()):
        return None
    return f"estruturas diferentes por corrente: {por_corrente}"


def _dialogo(id_dialogo: str, corrente: str, topicos: int) -> str:
    """Diálogo fictício: um início com `topicos` perguntas que voltam a ele e uma saída."""
    texto = f'[{id_dialogo}]\ninicio = "ola"\ncorrente = "{corrente}"\n'
    texto += f'[{id_dialogo}.nos.ola]\npassos = [{{ fala = "exemplo.ola" }}]\nopcoes = [\n'
    for n in range(topicos):
        texto += f'  {{ id = "t{n}", texto = "exemplo.t{n}", vai_para = "r{n}" }},\n'
    texto += '  { id = "tchau", texto = "exemplo.tchau", vai_para = "fim" },\n]\n'
    for n in range(topicos):
        texto += f'[{id_dialogo}.nos.r{n}]\npassos = [{{ fala = "exemplo.r{n}" }}]\n'
        texto += 'vai_para = "ola"\n'
    return texto


def test_e3_perfil_conta_opcoes_por_nivel():
    dialogo = Dialogos.de_toml(_dialogo("exemplo.a", "socialismo", 3))["exemplo.a"]
    assert perfil(dialogo) == ((4,), (0, 0, 0))


def test_e3_correntes_com_a_mesma_estrutura_passam():
    dialogos = Dialogos.de_toml("".join(_dialogo(f"exemplo.{c}", c, 3) for c in CORRENTES))
    assert desequilibrio_dos_dialogos(dialogos) is None


def test_e3_corrente_com_menos_topicos_e_acusada():
    topicos = {"liberalismo": 3, "conservadorismo": 3, "socialismo": 2, "social_democracia": 3}
    dialogos = Dialogos.de_toml("".join(_dialogo(f"exemplo.{c}", c, n) for c, n in topicos.items()))
    assert "socialismo" in desequilibrio_dos_dialogos(dialogos)


def test_e3_corrente_sem_personagem_e_acusada():
    dialogos = Dialogos.de_toml(
        "".join(_dialogo(f"exemplo.{c}", c, 3) for c in CORRENTES if c != "conservadorismo")
    )
    assert desequilibrio_dos_dialogos(dialogos) is not None


def test_e3_dialogo_sem_corrente_nao_entra_na_conta():
    textos = [_dialogo(f"exemplo.{c}", c, 3) for c in CORRENTES]
    textos.append(
        _dialogo("exemplo.vendedor", "liberalismo", 5).replace('corrente = "liberalismo"\n', "")
    )
    assert desequilibrio_dos_dialogos(Dialogos.de_toml("".join(textos))) is None


def test_e3_dialogos_do_jogo_tem_a_mesma_estrutura_por_corrente():
    assert desequilibrio_dos_dialogos(carregar_dialogos()) is None


# --- E5: manipulação distribuída por igual -----------------------------------------------------


def desequilibrio_da_manipulacao(casos: Casos) -> str | None:
    """Uma mensagem se os exemplos de manipulação não se distribuem por igual (E5)."""
    origens = Counter(caso.origem for caso in casos.values() if caso.classe is Classe.MANIPULACAO)
    if not origens:
        return None
    por_corrente = {corrente: origens[corrente] for corrente in CORRENTES}
    if len(set(por_corrente.values())) != 1:
        return f"manipulação desigual entre as correntes: {por_corrente}"
    if origens[SEM_LADO] == 0:
        return "falta pelo menos um exemplo de manipulação sem lado (golpe, caça-clique)"
    return None


def _manipulacoes(origens: list[str]) -> Casos:
    texto = "".join(
        f'[casos.exemplo.m{n}]\ntipo = "post"\nconteudo = "exemplo.m{n}"\nclasse = "manipulacao"\n'
        f'origem = "{origem}"\ntecnica = "caca_clique"\nexplicacao = "exemplo.e{n}"\n'
        for n, origem in enumerate(origens)
    )
    return Casos.de_toml(texto)


def test_e5_distribuicao_igual_com_sem_lado_passa():
    casos = _manipulacoes([*CORRENTES, *CORRENTES, SEM_LADO])
    assert desequilibrio_da_manipulacao(casos) is None


def test_e5_corrente_com_mais_exemplos_e_acusada():
    casos = _manipulacoes([*CORRENTES, "socialismo", SEM_LADO])
    assert "desigual" in desequilibrio_da_manipulacao(casos)


def test_e5_falta_exemplo_sem_lado_e_acusada():
    casos = _manipulacoes(list(CORRENTES))
    assert "sem lado" in desequilibrio_da_manipulacao(casos)


def test_e5_fatos_e_opinioes_nao_entram_na_conta():
    texto = (
        '[casos.exemplo.opiniao]\ntipo = "fala"\nconteudo = "exemplo.o"\nclasse = "opiniao"\n'
        'explicacao = "exemplo.oe"\n'
    )
    assert desequilibrio_da_manipulacao(Casos.de_toml(texto)) is None


def test_e5_manipulacao_do_jogo_distribuida_por_igual():
    assert desequilibrio_da_manipulacao(carregar_checagem()) is None
