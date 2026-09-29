"""Temporada - agrupa episodios de uma Serie."""

from __future__ import annotations

from src.models.episodio import Episodio


class Temporada:
    """Temporada de uma serie (composicao: contem Episodios).

    Atributos:
        numero: numero da temporada (> 0).
        episodios: lista de Episodio da temporada.
    """

    def __init__(self, numero: int, episodios: list[Episodio] | None = None) -> None:
        self.numero = numero
        self.episodios = episodios if episodios is not None else []

    def adicionar_episodio(self, episodio: Episodio) -> None:
        """Adiciona um episodio (numero de episodio nao pode repetir)."""
        raise NotImplementedError

    def todos_assistidos(self) -> bool:
        """True se todos os episodios da temporada estao ASSISTIDO."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
