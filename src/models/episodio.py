"""Episodio - fica dentro de uma Temporada."""

from __future__ import annotations

from datetime import date, datetime

from src.models.enums import StatusVisualizacao
from src.utils.validacoes import (
    validar_data,
    validar_data_hora_ou_none,
    validar_enum,
    validar_inteiro_positivo,
    validar_nota,
    validar_texto,
)


class Episodio:
    """Episodio de uma temporada.

    Atributos (todos validados por @property):
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

    @property
    def numero_temporada(self) -> int:
        """Numero da temporada (inteiro positivo)."""
        return self._numero_temporada

    @numero_temporada.setter
    def numero_temporada(self, valor: int) -> None:
        self._numero_temporada = validar_inteiro_positivo(valor, "O numero da temporada")

    @property
    def numero_episodio(self) -> int:
        """Numero do episodio (inteiro positivo)."""
        return self._numero_episodio

    @numero_episodio.setter
    def numero_episodio(self, valor: int) -> None:
        self._numero_episodio = validar_inteiro_positivo(valor, "O numero do episodio")

    @property
    def titulo(self) -> str:
        """Titulo do episodio (nao pode ser vazio)."""
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = validar_texto(valor, "O titulo do episodio")

    @property
    def duracao_minutos(self) -> int:
        """Duracao em minutos (maior que zero)."""
        return self._duracao_minutos

    @duracao_minutos.setter
    def duracao_minutos(self, valor: int) -> None:
        self._duracao_minutos = validar_inteiro_positivo(valor, "A duracao")

    @property
    def data_lancamento(self) -> date:
        """Data de lancamento do episodio."""
        return self._data_lancamento

    @data_lancamento.setter
    def data_lancamento(self, valor: date) -> None:
        self._data_lancamento = validar_data(valor, "A data de lancamento")

    @property
    def status(self) -> StatusVisualizacao:
        """Status de visualizacao (aceita o Enum ou o texto dele)."""
        return self._status

    @status.setter
    def status(self, valor: StatusVisualizacao) -> None:
        self._status = validar_enum(valor, StatusVisualizacao, "O status")

    @property
    def nota(self) -> float | None:
        """Nota de 0 a 10. Opcional: None significa 'sem nota'."""
        return self._nota

    @nota.setter
    def nota(self, valor: float | None) -> None:
        self._nota = None if valor is None else validar_nota(valor)

    @property
    def data_conclusao(self) -> datetime | None:
        """Data/hora em que o episodio foi assistido (None se nao foi)."""
        return self._data_conclusao

    @data_conclusao.setter
    def data_conclusao(self, valor: datetime | None) -> None:
        self._data_conclusao = validar_data_hora_ou_none(valor, "A data de conclusao")

    def marcar_assistido(self, quando: datetime | None = None) -> None:
        """Marca o episodio como ASSISTIDO e registra a data/hora.

        Se 'quando' nao for informado, usa o momento atual.
        """
        self.status = StatusVisualizacao.ASSISTIDO
        self.data_conclusao = quando if quando is not None else datetime.now()

    def __str__(self) -> str:
        """Ex.: T01E03 - Titulo do episodio (45 min) - ASSISTIDO"""
        return (
            f"T{self.numero_temporada:02d}E{self.numero_episodio:02d} - "
            f"{self.titulo} ({self.duracao_minutos} min) - {self.status.value}"
        )

    def __repr__(self) -> str:
        return (
            f"Episodio(temporada={self.numero_temporada}, "
            f"episodio={self.numero_episodio}, titulo={self.titulo!r})"
        )
