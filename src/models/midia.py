"""Classe base pra qualquer midia do catalogo (filme ou serie).

Filme e Serie herdam daqui. Implementacao (validacoes e logica) vem na semana 2.
"""

from __future__ import annotations

from datetime import datetime

from src.models.enums import StatusVisualizacao, TipoMidia


class Midia:
    """Midia generica do catalogo.

    Atributos:
        titulo: titulo da midia (nao pode ser vazio).
        tipo: TipoMidia.FILME ou TipoMidia.SERIE.
        genero: genero principal (ex.: "Drama", "Ficcao").
        ano: ano de lancamento.
        duracao_minutos: duracao em minutos (> 0). Em Serie fica None,
            porque a duracao vem da soma dos episodios.
        classificacao_indicativa: ex.: "L", "12", "16", "18".
        elenco: lista com nomes do elenco.
        status: StatusVisualizacao atual.
        nota: nota do usuario de 0 a 10 (None se ainda nao avaliada).
        data_conclusao: data/hora em que foi concluida (None se nao foi).

    Observacao: __eq__ compara por titulo + tipo, entao a classe precisa
    de __hash__ coerente se for usada em set/dict (decidir na semana 2).
    """

    def __init__(
        self,
        titulo: str,
        tipo: TipoMidia,
        genero: str,
        ano: int,
        duracao_minutos: int | None,
        classificacao_indicativa: str,
        elenco: list[str] | None = None,
        status: StatusVisualizacao = StatusVisualizacao.NAO_ASSISTIDO,
        nota: float | None = None,
        data_conclusao: datetime | None = None,
    ) -> None:
        self.titulo = titulo
        self.tipo = tipo
        self.genero = genero
        self.ano = ano
        self.duracao_minutos = duracao_minutos
        self.classificacao_indicativa = classificacao_indicativa
        self.elenco = elenco if elenco is not None else []
        self.status = status
        self.nota = nota
        self.data_conclusao = data_conclusao

    def duracao_total(self) -> int:
        """Duracao total em minutos (Filme: a propria; Serie: soma dos episodios)."""
        raise NotImplementedError

    def nota_media(self) -> float | None:
        """Nota usada em comparacoes e relatorios (Serie sobrescreve)."""
        raise NotImplementedError

    def marcar_concluida(self, quando: datetime | None = None) -> None:
        """Marca como ASSISTIDO e registra data/hora de conclusao."""
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __lt__(self, other: Midia) -> bool:
        raise NotImplementedError
