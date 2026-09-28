"""Serie - agrega temporadas."""

from __future__ import annotations

from src.models.midia import Midia
from src.models.temporada import Temporada


class Serie(Midia):
    def __init__(self) -> None:
        raise NotImplementedError

    def adicionar_temporada(self, temporada: Temporada) -> None:
        raise NotImplementedError

    def nota_media(self) -> float:
        raise NotImplementedError

    def atualizar_status(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
