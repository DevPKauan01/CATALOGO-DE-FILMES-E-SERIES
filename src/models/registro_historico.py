"""Um item do historico do usuario."""

from __future__ import annotations

from src.models.midia import Midia


class RegistroHistorico:
    def __init__(self) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError
