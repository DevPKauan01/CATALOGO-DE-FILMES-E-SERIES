"""Classe base pra qualquer midia do catalogo (filme ou serie).

Filme e Serie herdam daqui. Ainda vazia, implementacao vem na semana 2.
"""

from __future__ import annotations


class Midia:
    """
    Atributos que essa classe vai ter:
    titulo, tipo (FILME/SERIE), genero, ano, duracao_minutos,
    classificacao_indicativa, elenco, status, nota, data_conclusao
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def marcar_concluida(self) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __lt__(self, other: "Midia") -> bool:
        raise NotImplementedError
