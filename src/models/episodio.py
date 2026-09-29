"""Episodio - fica dentro de uma Temporada."""

from __future__ import annotations

from datetime import date, datetime

from src.models.enums import StatusVisualizacao


class Episodio:
    """Episodio de uma temporada.

    Atributos:
        numero_temporada: numero da temporada (> 0).
        numero_episodio: numero do episodio (> 0).
        titulo: titulo do episodio (nao pode ser vazio).
        duracao_minutos: duracao em minutos (> 0).
        data_lancamento: data de lancamento do episodio.
        status: StatusVisualizacao do episodio.
        nota: nota opcional de 0 a 10.
        data_conclusao: data/hora em que foi assistido (None se nao foi).
    """

    def __init__(
        self,
        numero_temporada: int,
        numero_episodio: int,
        titulo: str,
        duracao_minutos: int,
        data_lancamento: date,
        status: StatusVisualizacao = StatusVisualizacao.NAO_ASSISTIDO,
        nota: float | None = None,
        data_conclusao: datetime | None = None,
    ) -> None:
        self.numero_temporada = numero_temporada
        self.numero_episodio = numero_episodio
        self.titulo = titulo
        self.duracao_minutos = duracao_minutos
        self.data_lancamento = data_lancamento
        self.status = status
        self.nota = nota
        self.data_conclusao = data_conclusao

    def marcar_assistido(self, quando: datetime | None = None) -> None:
        """Marca o episodio como ASSISTIDO e registra a data/hora."""
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError
