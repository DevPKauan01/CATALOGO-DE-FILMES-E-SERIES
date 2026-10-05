"""Relatorios do catalogo. Consideram so midias ASSISTIDO."""

from __future__ import annotations

from datetime import datetime

from src.services.catalogo import Catalogo
from src.config.configuracoes import Configuracoes
from src.models.midia import Midia
from src.models.serie import Serie


def media_por_genero(catalogo: Catalogo) -> dict[str, float]:
    """Nota media por genero."""
    raise NotImplementedError


def tempo_assistido_por_tipo(
    catalogo: Catalogo, config: Configuracoes
) -> dict[str, float]:
    """Tempo total assistido (em horas) por tipo: FILME e SERIE."""
    raise NotImplementedError


def top_melhores(catalogo: Catalogo, limite: int = 10) -> list[Midia]:
    """Top N filmes/series mais bem avaliados."""
    raise NotImplementedError


def series_mais_assistidas(catalogo: Catalogo, limite: int = 10) -> list[Serie]:
    """Series com maior numero de episodios assistidos."""
    raise NotImplementedError


def tempo_assistido_no_periodo(
    catalogo: Catalogo,
    inicio: datetime,
    fim: datetime,
    config: Configuracoes,
) -> float:
    """Tempo total assistido (em horas) entre duas datas (semana/mes)."""
    raise NotImplementedError
