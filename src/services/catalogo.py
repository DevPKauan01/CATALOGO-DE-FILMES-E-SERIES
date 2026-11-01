"""Catalogo - guarda todas as midias e garante as regras globais."""

from __future__ import annotations

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.midia import Midia


class Catalogo:
    """Colecao de midias do catalogo pessoal.

    Relacionamento: agregacao com Midia (1 catalogo tem 0..* midias).

    Responsavel por impedir duplicidade (titulo + tipo + ano) e por servir
    de base pros relatorios.

    Atributos:
        midias: todas as midias cadastradas (so leitura, copia da lista).

    Cuidado: como existe __len__, um catalogo vazio tem len 0 e
    'if catalogo:' da False. Pra testar se existe, use 'is not None'.
    """

    def __init__(self, midias: list[Midia] | None = None) -> None:
        self._midias: list[Midia] = []
        for midia in midias if midias is not None else []:
            self.adicionar(midia)

    @property
    def midias(self) -> list[Midia]:
        """Midias cadastradas (copia, pra ninguem burlar o adicionar)."""
        return list(self._midias)

    def adicionar(self, midia: Midia) -> None:
        """Cadastra a midia; recusa se ja existir mesmo titulo + tipo + ano.

        Raises:
            ValueError: se nao for Midia ou se for duplicada.
        """
        if not isinstance(midia, Midia):
            raise ValueError("So e possivel adicionar objetos do tipo Midia.")
        if self.existe(midia.titulo, midia.tipo, midia.ano):
            raise ValueError(
                f"{midia.titulo!r} ({midia.ano}) ja esta cadastrado como "
                f"{midia.tipo.value}."
            )
        self._midias.append(midia)

    def obter(self, titulo: str, tipo: TipoMidia, ano: int) -> Midia | None:
        """Devolve a midia com esse titulo + tipo + ano (None se nao achar)."""
        for midia in self._midias:
            if (
                midia.titulo.lower() == titulo.strip().lower()
                and midia.tipo == tipo
                and midia.ano == ano
            ):
                return midia
        return None

    def existe(self, titulo: str, tipo: TipoMidia, ano: int) -> bool:
        """True se ja existe midia com esse titulo + tipo + ano."""
        return self.obter(titulo, tipo, ano) is not None

    def buscar(self, titulo: str, tipo: TipoMidia | None = None) -> list[Midia]:
        """Busca midias pelo titulo (e opcionalmente pelo tipo).

        A busca acha qualquer titulo que contenha o texto, sem diferenciar
        maiuscula de minuscula.
        """
        texto = titulo.strip().lower()
        return [
            midia
            for midia in self._midias
            if texto in midia.titulo.lower() and (tipo is None or midia.tipo == tipo)
        ]

    def concluidas(self) -> list[Midia]:
        """Midias com status ASSISTIDO (base dos relatorios)."""
        return [m for m in self._midias if m.status == StatusVisualizacao.ASSISTIDO]

    def nota_geral(self) -> float | None:
        """Nota media geral do catalogo (None se nao ha notas).

        Considera so midias concluidas (ASSISTIDO), como os demais relatorios.
        """
        notas = [m.nota_media() for m in self.concluidas() if m.nota_media() is not None]
        if len(notas) == 0:
            return None
        return sum(notas) / len(notas)

    def __len__(self) -> int:
        return len(self._midias)