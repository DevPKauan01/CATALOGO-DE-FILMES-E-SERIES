"""Filme - nao tem muito alem do que ja vem de Midia."""

from __future__ import annotations

from datetime import datetime

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.midia import Midia


class Filme(Midia):
    """Filme do catalogo. Usa duracao e nota direto da Midia.

    Fixa tipo = TipoMidia.FILME. Sem atributos extras por enquanto.
    """

    def __init__(
        self,
        titulo: str,
        genero: str,
        ano: int,
        duracao_minutos: int,
        classificacao_indicativa: str,
        elenco: list[str] | None = None,
        status: StatusVisualizacao = StatusVisualizacao.NAO_ASSISTIDO,
        nota: float | None = None,
        data_conclusao: datetime | None = None,
    ) -> None:
        super().__init__(
            titulo=titulo,
            tipo=TipoMidia.FILME,
            genero=genero,
            ano=ano,
            duracao_minutos=duracao_minutos,
            classificacao_indicativa=classificacao_indicativa,
            elenco=elenco,
            status=status,
            nota=nota,
            data_conclusao=data_conclusao,
        )
