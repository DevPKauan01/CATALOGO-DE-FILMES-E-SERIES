"""Classe base pra qualquer midia do catalogo (filme ou serie).

Filme e Serie herdam daqui. Aqui ficam os campos em comum, as validacoes
(@property) e os metodos especiais (__str__, __repr__, __eq__, __hash__, __lt__).
"""

from __future__ import annotations

from datetime import datetime

from src.models.enums import StatusVisualizacao, TipoMidia
from src.utils.validacoes import (
    validar_ano,
    validar_data_hora_ou_none,
    validar_enum,
    validar_inteiro_positivo,
    validar_nota,
    validar_texto,
)


class Midia:
    """Midia generica do catalogo.

    Atributos (todos validados por @property):
        titulo: titulo da midia (nao pode ser vazio).
        tipo: TipoMidia.FILME ou TipoMidia.SERIE (so leitura).
        genero: genero principal (ex.: "Drama", "Ficcao").
        ano: ano de lancamento.
        duracao_minutos: duracao em minutos (> 0). Em Serie fica None,
            porque a duracao vem da soma dos episodios.
        classificacao_indicativa: ex.: "L", "12", "16", "18".
        elenco: lista com nomes do elenco.
        status: StatusVisualizacao atual.
        nota: nota do usuario de 0 a 10 (None se ainda nao avaliada).
        data_conclusao: data/hora em que foi concluida (None se nao foi).

    __eq__ compara por titulo + tipo (sem diferenciar maiuscula/minuscula).
    Como definimos __eq__, tambem definimos __hash__ coerente com ele,
    assim a midia pode ser usada em set e dict.
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
        self._tipo = validar_enum(tipo, TipoMidia, "O tipo")
        self.genero = genero
        self.ano = ano
        # Serie passa None aqui (duracao vem dos episodios), entao so valida se veio valor
        self._duracao_minutos = None
        if duracao_minutos is not None:
            self.duracao_minutos = duracao_minutos
        self.classificacao_indicativa = classificacao_indicativa
        self.elenco = elenco if elenco is not None else []
        self.status = status
        self._nota = None
        if nota is not None:
            self.nota = nota
        self.data_conclusao = data_conclusao

    # ------------------------------------------------------------------
    # Propriedades (encapsulamento + validacao)
    # ------------------------------------------------------------------
    @property
    def titulo(self) -> str:
        """Titulo da midia (nao pode ser vazio)."""
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = validar_texto(valor, "O titulo")

    @property
    def tipo(self) -> TipoMidia:
        """Tipo da midia. So leitura: nao muda depois de criada."""
        return self._tipo

    @property
    def genero(self) -> str:
        """Genero da midia (nao pode ser vazio)."""
        return self._genero

    @genero.setter
    def genero(self, valor: str) -> None:
        self._genero = validar_texto(valor, "O genero")

    @property
    def ano(self) -> int:
        """Ano de lancamento (inteiro, no minimo 1888)."""
        return self._ano

    @ano.setter
    def ano(self, valor: int) -> None:
        self._ano = validar_ano(valor)

    @property
    def duracao_minutos(self) -> int | None:
        """Duracao em minutos (maior que zero)."""
        return self._duracao_minutos

    @duracao_minutos.setter
    def duracao_minutos(self, valor: int) -> None:
        self._duracao_minutos = validar_inteiro_positivo(valor, "A duracao")

    @property
    def classificacao_indicativa(self) -> str:
        """Classificacao indicativa (ex.: "L", "12", "18")."""
        return self._classificacao_indicativa

    @classificacao_indicativa.setter
    def classificacao_indicativa(self, valor: str) -> None:
        self._classificacao_indicativa = validar_texto(valor, "A classificacao indicativa")

    @property
    def elenco(self) -> list[str]:
        """Lista com os nomes do elenco.

        Devolve uma COPIA da lista: quem usa a classe nao consegue mexer no
        elenco "por fora" sem passar pelo setter (que valida).
        """
        return list(self._elenco)

    @elenco.setter
    def elenco(self, valor: list[str]) -> None:
        if not isinstance(valor, (list, tuple)):
            raise ValueError("O elenco deve ser uma lista de nomes.")
        self._elenco = [validar_texto(nome, "O nome do ator") for nome in valor]

    @property
    def status(self) -> StatusVisualizacao:
        """Status de visualizacao (aceita o Enum ou o texto dele)."""
        return self._status

    @status.setter
    def status(self, valor: StatusVisualizacao) -> None:
        self._status = validar_enum(valor, StatusVisualizacao, "O status")

    @property
    def nota(self) -> float | None:
        """Nota de 0 a 10 (None se ainda nao avaliada)."""
        return self._nota

    @nota.setter
    def nota(self, valor: float | None) -> None:
        # None serve pra "remover" a nota
        self._nota = None if valor is None else validar_nota(valor)

    @property
    def data_conclusao(self) -> datetime | None:
        """Data/hora em que a midia foi concluida (None se nao foi)."""
        return self._data_conclusao

    @data_conclusao.setter
    def data_conclusao(self, valor: datetime | None) -> None:
        self._data_conclusao = validar_data_hora_ou_none(valor, "A data de conclusao")

    # ------------------------------------------------------------------
    # Metodos normais
    # ------------------------------------------------------------------
    def duracao_total(self) -> int:
        """Duracao total em minutos (Filme: a propria; Serie: soma dos episodios)."""
        if self.duracao_minutos is None:
            return 0
        return self.duracao_minutos

    def nota_media(self) -> float | None:
        """Nota usada em comparacoes e relatorios (Serie sobrescreve)."""
        return self.nota

    def marcar_concluida(self, quando: datetime | None = None) -> None:
        """Marca como ASSISTIDO e registra data/hora de conclusao.

        Se 'quando' nao for informado, usa o momento atual.
        """
        self.status = StatusVisualizacao.ASSISTIDO
        self.data_conclusao = quando if quando is not None else datetime.now()

    # ------------------------------------------------------------------
    # Metodos especiais
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        """Texto formatado pra mostrar ao usuario (print)."""
        nota = self.nota_media()
        texto_nota = f"nota {nota:.1f}" if nota is not None else "sem nota"
        return (
            f"[{self.tipo.value}] {self.titulo} ({self.ano}) - {self.genero} - "
            f"{self.duracao_total()} min - {texto_nota} - {self.status.value}"
        )

    def __repr__(self) -> str:
        """Texto tecnico, aparece quando imprime listas e no debug."""
        return f"{self.__class__.__name__}(titulo={self.titulo!r}, ano={self.ano!r})"

    def _chave(self) -> tuple[str, TipoMidia]:
        """Par (titulo, tipo) usado pra comparar midias."""
        return (self.titulo.lower(), self.tipo)

    def __eq__(self, other: object) -> bool:
        """Duas midias sao iguais se tem o mesmo titulo e o mesmo tipo."""
        if not isinstance(other, Midia):
            return NotImplemented
        return self._chave() == other._chave()

    def __hash__(self) -> int:
        """Obrigatorio quando se define __eq__ (coerente com ele)."""
        return hash(self._chave())

    def __lt__(self, other: Midia) -> bool:
        """Ordena por nota media (menor < maior). Sem nota conta como 0.

        Com isso da pra usar sorted(lista_de_midias) direto.
        """
        if not isinstance(other, Midia):
            return NotImplemented
        nota_self = self.nota_media() if self.nota_media() is not None else 0
        nota_other = other.nota_media() if other.nota_media() is not None else 0
        return nota_self < nota_other
