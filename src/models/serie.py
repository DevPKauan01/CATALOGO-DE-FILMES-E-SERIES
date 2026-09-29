"""Serie - agrega temporadas."""

from __future__ import annotations

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.midia import Midia
from src.models.temporada import Temporada


class Serie(Midia):
    """Serie do catalogo (composicao: contem Temporadas).

    Fixa tipo = TipoMidia.SERIE. A duracao e a nota nao sao informadas
    diretamente: sao calculadas a partir dos episodios. O status vira
    ASSISTIDO sozinho quando todos os episodios forem assistidos.

    Atributos extras:
        temporadas: lista de Temporada da serie.
    """

    def __init__(
        self,
        titulo: str,
        genero: str,
        ano: int,
        classificacao_indicativa: str,
        elenco: list[str] | None = None,
        status: StatusVisualizacao = StatusVisualizacao.NAO_ASSISTIDO,
        temporadas: list[Temporada] | None = None,
    ) -> None:
        super().__init__(
            titulo=titulo,
            tipo=TipoMidia.SERIE,
            genero=genero,
            ano=ano,
            duracao_minutos=None,
            classificacao_indicativa=classificacao_indicativa,
            elenco=elenco,
            status=status,
        )
        self.temporadas = temporadas if temporadas is not None else []

    def adicionar_temporada(self, temporada: Temporada) -> None:
        """Adiciona uma temporada (numero de temporada nao pode repetir)."""
        raise NotImplementedError

    def episodios_assistidos(self) -> int:
        """Quantidade de episodios com status ASSISTIDO."""
        raise NotImplementedError

    def nota_media(self) -> float | None:
        """Media das notas dos episodios avaliados (None se nenhum)."""
        raise NotImplementedError

    def atualizar_status(self) -> None:
        """Vira ASSISTIDA quando todos os episodios estiverem ASSISTIDO."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Numero total de episodios da serie."""
        raise NotImplementedError
