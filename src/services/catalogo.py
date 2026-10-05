"""Catalogo - guarda todas as midias e garante as regras globais."""

from __future__ import annotations

from src.models.enums import TipoMidia
from src.models.midia import Midia


class Catalogo:
    """Colecao de midias do catalogo pessoal.

    Responsavel por impedir duplicidade (titulo + tipo + ano) e por servir
    de base pros relatorios.

    Atributos:
        midias: todas as midias cadastradas.
    """

    def __init__(self, midias: list[Midia] | None = None) -> None:
        self.midias = midias if midias is not None else []

    def adicionar(self, midia: Midia) -> None:
        """Cadastra a midia; recusa se ja existir mesmo titulo + tipo + ano."""
        raise NotImplementedError

    def existe(self, titulo: str, tipo: TipoMidia, ano: int) -> bool:
        """True se ja existe midia com esse titulo + tipo + ano."""
        raise NotImplementedError

    def buscar(self, titulo: str, tipo: TipoMidia | None = None) -> list[Midia]:
        """Busca midias pelo titulo (e opcionalmente pelo tipo)."""
        raise NotImplementedError

    def concluidas(self) -> list[Midia]:
        """Midias com status ASSISTIDO (base dos relatorios)."""
        raise NotImplementedError

    def nota_geral(self) -> float | None:
        """Nota media geral do catalogo (None se nao ha notas)."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
