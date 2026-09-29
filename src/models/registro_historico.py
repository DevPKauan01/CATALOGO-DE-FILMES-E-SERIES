"""Um item do historico do usuario."""

from __future__ import annotations

from datetime import datetime

from src.models.midia import Midia


class RegistroHistorico:
    """Registro de conclusao de uma midia.

    Atributos:
        midia: midia concluida.
        data_conclusao: data/hora em que foi concluida.
    """

    def __init__(self, midia: Midia, data_conclusao: datetime) -> None:
        self.midia = midia
        self.data_conclusao = data_conclusao

    def __str__(self) -> str:
        raise NotImplementedError
