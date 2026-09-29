"""Enumeracoes usadas pelo dominio (evita strings soltas pelo codigo)."""

from __future__ import annotations

from enum import Enum


class TipoMidia(Enum):
    """Tipo de uma midia do catalogo."""

    FILME = "FILME"
    SERIE = "SERIE"


class StatusVisualizacao(Enum):
    """Status de visualizacao de uma midia ou de um episodio."""

    NAO_ASSISTIDO = "NÃO ASSISTIDO"
    ASSISTINDO = "ASSISTINDO"
    ASSISTIDO = "ASSISTIDO"
