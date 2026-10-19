"""Lista personalizada tipo Favoritos ou Pra assistir."""

from __future__ import annotations

from src.models.midia import Midia
from src.utils.validacoes import validar_texto


class ListaPersonalizada:
    """Lista nomeada de midias criada pelo usuario.

    Relacionamento: associacao com Midia (a lista so referencia as midias,
    quem guarda elas de verdade e o Catalogo).

    Atributos:
        nome: nome da lista (nao pode ser vazio).
        midias: midias da lista (sem repetir; so leitura, copia da lista).

    Cuidado: como existe __len__, uma lista vazia tem len 0 e
    'if lista:' da False. Pra testar se existe, use 'is not None'.
    """

    def __init__(self, nome: str, midias: list[Midia] | None = None) -> None:
        self.nome = nome
        self._midias: list[Midia] = []
        for midia in midias if midias is not None else []:
            self.adicionar(midia)

    @property
    def nome(self) -> str:
        """Nome da lista (nao pode ser vazio)."""
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        self._nome = validar_texto(valor, "O nome da lista")

    @property
    def midias(self) -> list[Midia]:
        """Midias da lista (copia, pra ninguem burlar o adicionar)."""
        return list(self._midias)

    def adicionar(self, midia: Midia) -> None:
        """Adiciona a midia na lista.

        Raises:
            ValueError: se nao for Midia ou se ja estiver na lista.
        """
        if not isinstance(midia, Midia):
            raise ValueError("So e possivel adicionar objetos do tipo Midia.")
        if midia in self._midias:
            raise ValueError(f"{midia.titulo!r} ja esta na lista {self.nome!r}.")
        self._midias.append(midia)

    def remover(self, midia: Midia) -> None:
        """Remove a midia da lista.

        Raises:
            ValueError: se a midia nao estiver na lista.
        """
        if midia not in self._midias:
            raise ValueError(f"A midia nao esta na lista {self.nome!r}.")
        self._midias.remove(midia)

    def __len__(self) -> int:
        return len(self._midias)

    def __str__(self) -> str:
        return f"{self.nome} ({len(self)} midias)"

    def __repr__(self) -> str:
        return f"ListaPersonalizada(nome={self.nome!r})"
