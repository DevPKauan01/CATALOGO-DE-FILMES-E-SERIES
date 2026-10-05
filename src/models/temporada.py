"""Temporada - agrupa episodios de uma Serie."""

from __future__ import annotations

from src.models.enums import StatusVisualizacao
from src.models.episodio import Episodio
from src.utils.validacoes import validar_inteiro_positivo


class Temporada:
    """Temporada de uma serie (composicao: contem Episodios).

    Atributos:
        numero: numero da temporada (> 0).
        episodios: lista de Episodio da temporada (so leitura; pra incluir
            use adicionar_episodio).
    """

    def __init__(self, numero: int, episodios: list[Episodio] | None = None) -> None:
        self.numero = numero
        self._episodios: list[Episodio] = []
        # Passa por adicionar_episodio pra aplicar as mesmas regras
        for episodio in episodios if episodios is not None else []:
            self.adicionar_episodio(episodio)

    @property
    def numero(self) -> int:
        """Numero da temporada (inteiro positivo)."""
        return self._numero

    @numero.setter
    def numero(self, valor: int) -> None:
        self._numero = validar_inteiro_positivo(valor, "O numero da temporada")

    @property
    def episodios(self) -> list[Episodio]:
        """Lista dos episodios (copia, pra ninguem mexer na lista original)."""
        return list(self._episodios)

    def adicionar_episodio(self, episodio: Episodio) -> None:
        """Adiciona um episodio (numero de episodio nao pode repetir).

        Regras:
          - tem que ser um objeto Episodio;
          - o numero_temporada dele tem que ser o desta temporada;
          - nao pode ja existir um episodio com o mesmo numero.

        Raises:
            ValueError: se alguma regra for violada.
        """
        if not isinstance(episodio, Episodio):
            raise ValueError("So e possivel adicionar objetos do tipo Episodio.")
        if episodio.numero_temporada != self.numero:
            raise ValueError(
                f"O episodio e da temporada {episodio.numero_temporada}, "
                f"mas esta e a temporada {self.numero}."
            )
        for existente in self._episodios:
            if existente.numero_episodio == episodio.numero_episodio:
                raise ValueError(
                    f"A temporada {self.numero} ja tem o episodio "
                    f"{episodio.numero_episodio}."
                )
        self._episodios.append(episodio)
        # Mantem em ordem (1, 2, 3...)
        self._episodios.sort(key=lambda ep: ep.numero_episodio)

    def duracao_total(self) -> int:
        """Soma da duracao dos episodios, em minutos."""
        return sum(ep.duracao_minutos for ep in self._episodios)

    def todos_assistidos(self) -> bool:
        """True se todos os episodios da temporada estao ASSISTIDO.

        Temporada sem episodios devolve False (nao ha nada pra ter assistido).
        """
        if len(self._episodios) == 0:
            return False
        return all(ep.status == StatusVisualizacao.ASSISTIDO for ep in self._episodios)

    def __len__(self) -> int:
        """Quantidade de episodios da temporada."""
        return len(self._episodios)

    def __str__(self) -> str:
        return f"Temporada {self.numero} ({len(self)} episodios)"

    def __repr__(self) -> str:
        return f"Temporada(numero={self.numero})"
