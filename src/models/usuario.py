"""Usuario - dono das listas e do historico."""

from __future__ import annotations

from src.models.lista_personalizada import ListaPersonalizada
from src.models.midia import Midia


class Usuario:
    def __init__(self) -> None:
        raise NotImplementedError

    def criar_lista(self, nome: str) -> ListaPersonalizada:
        raise NotImplementedError

    def adicionar_favorito(self, midia: Midia, nome_lista: str) -> None:
        raise NotImplementedError

    def registrar_conclusao(self, midia: Midia) -> None:
        raise NotImplementedError
