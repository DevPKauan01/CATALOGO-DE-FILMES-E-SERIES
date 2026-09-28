"""Temporada - agrupa episodios de uma Serie."""

from __future__ import annotations

from src.models.episodio import Episodio


class Temporada:
    def __init__(self) -> None:
        raise NotImplementedError

    def adicionar_episodio(self, episodio: Episodio) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
