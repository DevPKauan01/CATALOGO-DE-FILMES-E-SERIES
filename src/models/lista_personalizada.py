"""Lista personalizada tipo Favoritos ou Pra assistir."""

from __future__ import annotations

from src.models.midia import Midia


class ListaPersonalizada:
    """Lista nomeada de midias criada pelo usuario.

    Atributos:
        nome: nome da lista (nao pode ser vazio).
        midias: midias da lista (sem repetir).
    """

    def __init__(self, nome: str, midias: list[Midia] | None = None) -> None:
        self.nome = nome
        self.midias = midias if midias is not None else []

    def adicionar(self, midia: Midia) -> None:
        """Adiciona a midia na lista (ignora/recusa se ja estiver)."""
        raise NotImplementedError

    def remover(self, midia: Midia) -> None:
        """Remove a midia da lista."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
