"""Lista personalizada tipo Favoritos ou Pra assistir."""

from __future__ import annotations

from src.models.midia import Midia


class ListaPersonalizada:
    def __init__(self) -> None:
        raise NotImplementedError

    def adicionar(self, midia: Midia) -> None:
        raise NotImplementedError

    def remover(self, midia: Midia) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
