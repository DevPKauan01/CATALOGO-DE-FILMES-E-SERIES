"""Um item do historico do usuario."""

from __future__ import annotations

from datetime import datetime

from src.models.midia import Midia
from src.utils.validacoes import validar_data_hora_ou_none


class RegistroHistorico:
    """Registro de conclusao de uma midia.

    Relacionamento: associacao com Midia (o registro referencia 1 midia).

    Atributos:
        midia: midia concluida.
        data_conclusao: data/hora em que foi concluida.
    """

    def __init__(self, midia: Midia, data_conclusao: datetime) -> None:
        self.midia = midia
        self.data_conclusao = data_conclusao

    @property
    def midia(self) -> Midia:
        """Midia que foi concluida."""
        return self._midia

    @midia.setter
    def midia(self, valor: Midia) -> None:
        if not isinstance(valor, Midia):
            raise ValueError("O registro precisa de uma midia.")
        self._midia = valor

    @property
    def data_conclusao(self) -> datetime:
        """Data/hora da conclusao (obrigatoria no historico)."""
        return self._data_conclusao

    @data_conclusao.setter
    def data_conclusao(self, valor: datetime) -> None:
        if valor is None:
            raise ValueError("A data de conclusao nao pode ser vazia.")
        self._data_conclusao = validar_data_hora_ou_none(valor, "A data de conclusao")

    def __str__(self) -> str:
        """Ex.: 05/10/2026 20:41 - Interestelar (FILME)"""
        return (
            f"{self.data_conclusao:%d/%m/%Y %H:%M} - "
            f"{self.midia.titulo} ({self.midia.tipo.value})"
        )

    def __repr__(self) -> str:
        return f"RegistroHistorico(midia={self.midia.titulo!r})"
