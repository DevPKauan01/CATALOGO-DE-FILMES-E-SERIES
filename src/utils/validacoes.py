"""Funcoes de validacao reutilizadas pelos setters (@property) das classes.

Padrao de todas elas:
  - valor valido   -> devolvem o valor (ja "limpo");
  - valor invalido -> lancam ValueError explicando o problema.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

NOTA_MINIMA = 0
NOTA_MAXIMA = 10
ANO_MINIMO = 1888  # ano do primeiro filme da historia


def validar_texto(valor: object, nome_campo: str) -> str:
    """Garante que e uma string nao vazia e tira espacos das pontas."""
    if not isinstance(valor, str) or valor.strip() == "":
        raise ValueError(f"{nome_campo} nao pode ser vazio.")
    return valor.strip()


def validar_inteiro_positivo(valor: object, nome_campo: str) -> int:
    """Garante que e um inteiro maior que zero (bool nao vale)."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError(f"{nome_campo} deve ser um numero inteiro positivo.")
    return valor


def validar_ano(valor: object) -> int:
    """Garante que o ano e inteiro positivo e nao menor que ANO_MINIMO."""
    validar_inteiro_positivo(valor, "O ano")
    if valor < ANO_MINIMO:
        raise ValueError(f"O ano nao pode ser menor que {ANO_MINIMO}.")
    return valor


def validar_nota(valor: object) -> float:
    """Garante que a nota e numerica e esta entre 0 e 10."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError("A nota deve ser numerica.")
    if valor < NOTA_MINIMA or valor > NOTA_MAXIMA:
        raise ValueError(f"A nota deve estar entre {NOTA_MINIMA} e {NOTA_MAXIMA}.")
    return float(valor)


def validar_enum(valor: object, classe_enum: type[Enum], nome_campo: str) -> Enum:
    """Garante que o valor e um item do Enum.

    Aceita o proprio item (StatusVisualizacao.ASSISTIDO) ou o texto dele
    ("ASSISTIDO"), o que ajuda na hora de ler dados de um JSON.
    """
    if isinstance(valor, classe_enum):
        return valor
    try:
        return classe_enum(valor)
    except (ValueError, TypeError):
        raise ValueError(f"{nome_campo} invalido: {valor!r}.") from None


def validar_data(valor: object, nome_campo: str) -> date:
    """Garante que e um objeto date (datetime tambem serve)."""
    if not isinstance(valor, date):
        raise ValueError(f"{nome_campo} deve ser uma data (datetime.date).")
    return valor


def validar_data_hora_ou_none(valor: object, nome_campo: str) -> datetime | None:
    """Garante que e um datetime ou None."""
    if valor is not None and not isinstance(valor, datetime):
        raise ValueError(f"{nome_campo} deve ser um datetime (ou None).")
    return valor
