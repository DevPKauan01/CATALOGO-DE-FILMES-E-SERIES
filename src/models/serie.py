"""Serie - agrega temporadas."""

from __future__ import annotations

from datetime import datetime

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.episodio import Episodio
from src.models.midia import Midia
from src.models.temporada import Temporada


class Serie(Midia):
    """Serie do catalogo (composicao: contem Temporadas).

    Fixa tipo = TipoMidia.SERIE. A duracao e a nota nao sao informadas
    diretamente: sao calculadas a partir dos episodios. O status vira
    ASSISTIDO sozinho quando todos os episodios forem assistidos.

    Atributos extras:
        temporadas: lista de Temporada da serie (so leitura; pra incluir
            use adicionar_temporada ou adicionar_episodio).

    Sobre o status: ele fica guardado, e o metodo atualizar_status()
    recalcula a partir dos episodios. Ele e chamado sozinho ao adicionar
    temporada/episodio e em marcar_concluida(). Se voce marcar um episodio
    como assistido direto (episodio.marcar_assistido()), chame
    serie.atualizar_status() depois (e o que o subcomando
    'serie atualizar-status' da CLI vai fazer).

    Cuidado: como existe __len__, uma serie sem episodios tem len 0 e
    'if serie:' da False. Pra testar se existe, use 'is not None'.
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
        self._temporadas: list[Temporada] = []
        for temporada in temporadas if temporadas is not None else []:
            self.adicionar_temporada(temporada)

    # ------------------------------------------------------------------
    # Temporadas e episodios
    # ------------------------------------------------------------------
    @property
    def temporadas(self) -> list[Temporada]:
        """Temporadas em ordem de numero (copia da lista)."""
        return sorted(self._temporadas, key=lambda t: t.numero)

    def adicionar_temporada(self, temporada: Temporada) -> None:
        """Adiciona uma temporada (numero de temporada nao pode repetir).

        Raises:
            ValueError: se nao for Temporada ou se o numero ja existir.
        """
        if not isinstance(temporada, Temporada):
            raise ValueError("So e possivel adicionar objetos do tipo Temporada.")
        if self._buscar_temporada(temporada.numero) is not None:
            raise ValueError(f"A serie ja tem a temporada {temporada.numero}.")
        self._temporadas.append(temporada)
        self.atualizar_status()

    def adicionar_episodio(self, episodio: Episodio) -> None:
        """Adiciona um episodio na temporada certa.

        Se a temporada ainda nao existir, ela e criada automaticamente.

        Raises:
            ValueError: se nao for Episodio ou se o numero ja existir.
        """
        if not isinstance(episodio, Episodio):
            raise ValueError("So e possivel adicionar objetos do tipo Episodio.")
        temporada = self._buscar_temporada(episodio.numero_temporada)
        if temporada is None:
            temporada = Temporada(episodio.numero_temporada)
            self._temporadas.append(temporada)
        temporada.adicionar_episodio(episodio)
        self.atualizar_status()

    def _buscar_temporada(self, numero: int) -> Temporada | None:
        """Procura uma temporada pelo numero (None se nao achar)."""
        for temporada in self._temporadas:
            if temporada.numero == numero:
                return temporada
        return None

    def todos_episodios(self) -> list[Episodio]:
        """Lista com os episodios de todas as temporadas, em ordem."""
        episodios: list[Episodio] = []
        for temporada in self.temporadas:
            episodios.extend(temporada.episodios)
        return episodios

    def episodios_assistidos(self) -> int:
        """Quantidade de episodios com status ASSISTIDO."""
        return sum(
            1 for ep in self.todos_episodios()
            if ep.status == StatusVisualizacao.ASSISTIDO
        )

    # ------------------------------------------------------------------
    # Valores calculados
    # ------------------------------------------------------------------
    def duracao_total(self) -> int:
        """Soma da duracao de todos os episodios, em minutos."""
        return sum(ep.duracao_minutos for ep in self.todos_episodios())

    def nota_media(self) -> float | None:
        """Media das notas dos episodios avaliados (None se nenhum).

        Episodios sem nota sao ignorados no calculo.
        """
        notas = [ep.nota for ep in self.todos_episodios() if ep.nota is not None]
        if len(notas) == 0:
            return None
        return sum(notas) / len(notas)

    @property
    def nota(self) -> float | None:
        """Nota da serie = nota media dos episodios (so leitura)."""
        return self.nota_media()

    def atualizar_status(self) -> None:
        """Recalcula o status a partir dos episodios.

        - sem episodios                    -> NAO_ASSISTIDO
        - todos os episodios ASSISTIDO     -> ASSISTIDO (data = ultimo episodio)
        - algum episodio ja comecado/visto -> ASSISTINDO
        - nenhum comecado                  -> NAO_ASSISTIDO
        """
        episodios = self.todos_episodios()
        if len(episodios) == 0:
            self.status = StatusVisualizacao.NAO_ASSISTIDO
            self.data_conclusao = None
        elif self.episodios_assistidos() == len(episodios):
            self.status = StatusVisualizacao.ASSISTIDO
            datas = [ep.data_conclusao for ep in episodios if ep.data_conclusao is not None]
            self.data_conclusao = max(datas) if datas else datetime.now()
        else:
            comecou = any(
                ep.status != StatusVisualizacao.NAO_ASSISTIDO for ep in episodios
            )
            self.status = (
                StatusVisualizacao.ASSISTINDO if comecou
                else StatusVisualizacao.NAO_ASSISTIDO
            )
            self.data_conclusao = None

    def marcar_concluida(self, quando: datetime | None = None) -> None:
        """Marca todos os episodios como assistidos (a serie vira ASSISTIDO)."""
        for episodio in self.todos_episodios():
            episodio.marcar_assistido(quando)
        self.atualizar_status()

    # ------------------------------------------------------------------
    # Metodos especiais
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        """Numero total de episodios da serie (soma de todas as temporadas)."""
        return len(self.todos_episodios())

    def __str__(self) -> str:
        return f"{super().__str__()} - {len(self)} episodios"
