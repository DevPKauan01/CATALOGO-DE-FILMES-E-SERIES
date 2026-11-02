"""Sistema - junta catalogo, usuario e configuracoes e aplica as regras de negocio.

A CLI so le os argumentos e chama os metodos daqui. Assim as regras ficam em
um lugar so e podem ser testadas sem passar pela linha de comando.

Regras que passam por aqui (alem das validacoes que ja ficam nos @property):
    - duplicidade: mesmo titulo + tipo + ano nao pode ser cadastrado de novo;
    - so e possivel avaliar o que ja foi assistido (filme ou episodio);
    - series sao avaliadas por episodio (a nota da serie e a media);
    - a serie vira ASSISTIDO sozinha quando todos os episodios forem assistidos;
    - o historico acompanha o status (concluiu -> registra; deixou de estar
      concluida -> remove o registro);
    - a data de conclusao nao pode estar no futuro;
    - o limite de listas vem do settings.json.
"""

from __future__ import annotations

import os
from datetime import date, datetime

from src.config.configuracoes import Configuracoes
from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.episodio import Episodio
from src.models.filme import Filme
from src.models.lista_personalizada import ListaPersonalizada
from src.models.midia import Midia
from src.models.serie import Serie
from src.models.usuario import Usuario
from src.persistence.dados import (
    carregar_catalogo,
    carregar_usuario,
    salvar_catalogo,
    salvar_usuario,
    seed,
    seed_usuario,
)
from src.services.catalogo import Catalogo
from src.utils.validacoes import validar_enum, validar_nota


class Sistema:
    """Fachada do catalogo: operacoes de alto nivel usadas pela CLI.

    Atributos:
        catalogo: todas as midias cadastradas.
        usuario: usuario dono das listas e do historico.
        config: configuracoes lidas do settings.json.
        pasta_dados: pasta onde ficam os JSONs (catalogo.json e usuario.json).
    """

    ARQUIVO_CATALOGO = "catalogo.json"
    ARQUIVO_USUARIO = "usuario.json"

    def __init__(
        self,
        catalogo: Catalogo,
        usuario: Usuario,
        config: Configuracoes,
        pasta_dados: str = "dados",
    ) -> None:
        self.catalogo = catalogo
        self.usuario = usuario
        self.config = config
        self.pasta_dados = pasta_dados

    # ------------------------------------------------------------------
    # Abrir / salvar
    # ------------------------------------------------------------------
    @classmethod
    def abrir(
        cls, pasta_dados: str = "dados", caminho_settings: str = "settings.json"
    ) -> Sistema:
        """Carrega os dados da pasta. Na primeira vez (sem catalogo.json) usa o seed."""
        config = Configuracoes.carregar(caminho_settings)
        caminho_catalogo = os.path.join(pasta_dados, cls.ARQUIVO_CATALOGO)
        caminho_usuario = os.path.join(pasta_dados, cls.ARQUIVO_USUARIO)

        if not os.path.exists(caminho_catalogo):
            return cls.novo_com_seed(pasta_dados, config)

        catalogo = carregar_catalogo(caminho_catalogo)
        if os.path.exists(caminho_usuario):
            usuario = carregar_usuario(caminho_usuario, catalogo, config)
        else:
            usuario = Usuario("Usuario", config)
        return cls(catalogo, usuario, config, pasta_dados)

    @classmethod
    def novo_com_seed(cls, pasta_dados: str, config: Configuracoes) -> Sistema:
        """Cria um sistema com as midias pre-cadastradas e ja salva em disco."""
        catalogo = seed()
        usuario = seed_usuario(catalogo, config)
        sistema = cls(catalogo, usuario, config, pasta_dados)
        sistema.salvar()
        return sistema

    def salvar(self) -> None:
        """Grava catalogo e usuario na pasta de dados."""
        salvar_catalogo(
            self.catalogo, os.path.join(self.pasta_dados, self.ARQUIVO_CATALOGO)
        )
        salvar_usuario(
            self.usuario, os.path.join(self.pasta_dados, self.ARQUIVO_USUARIO)
        )

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def resolver_midia(
        self, titulo: str, tipo: TipoMidia | None = None, ano: int | None = None
    ) -> Midia:
        """Acha UMA midia pelo titulo (e, se precisar, tipo e ano).

        Primeiro tenta o titulo exato (sem diferenciar maiuscula); se nao achar,
        aceita um pedaco do titulo. Se sobrar mais de uma candidata, pede pra
        informar tipo/ano em vez de escolher uma por conta propria.

        Raises:
            ValueError: se nao achar nenhuma ou se ficar ambiguo.
        """
        texto = titulo.strip().lower()

        def filtrar(midias: list[Midia]) -> list[Midia]:
            return [m for m in midias if ano is None or m.ano == ano]

        exatas = filtrar(
            [m for m in self.catalogo.buscar(titulo, tipo) if m.titulo.lower() == texto]
        )
        candidatas = exatas or filtrar(self.catalogo.buscar(titulo, tipo))
        if len(candidatas) == 0:
            raise ValueError(f"Nenhuma midia encontrada para {titulo!r}.")
        if len(candidatas) > 1:
            opcoes = "; ".join(f"{m.titulo} ({m.ano}, {m.tipo.value})" for m in candidatas)
            raise ValueError(
                f"Mais de uma midia encontrada para {titulo!r}: {opcoes}. "
                "Use --tipo e/ou --ano pra escolher."
            )
        return candidatas[0]

    def _resolver_serie(self, titulo: str, ano: int | None = None) -> Serie:
        midia = self.resolver_midia(titulo, TipoMidia.SERIE, ano)
        assert isinstance(midia, Serie)  # tipo SERIE sempre e Serie
        return midia

    @staticmethod
    def _validar_conclusao(quando: datetime | None) -> None:
        """A data de conclusao nao pode estar no futuro."""
        if quando is not None and quando > datetime.now():
            raise ValueError("A data de conclusao nao pode ser no futuro.")

    # ------------------------------------------------------------------
    # Cadastro de midias
    # ------------------------------------------------------------------
    def adicionar_filme(
        self,
        titulo: str,
        genero: str,
        ano: int,
        duracao_minutos: int,
        classificacao: str,
        elenco: list[str] | None = None,
        status: StatusVisualizacao | str = StatusVisualizacao.NAO_ASSISTIDO,
        data_conclusao: datetime | None = None,
    ) -> Filme:
        """Cadastra um filme. Se ja entrar ASSISTIDO, registra a conclusao no historico.

        Raises:
            ValueError: dados invalidos, duplicidade ou data de conclusao no futuro.
        """
        status = validar_enum(status, StatusVisualizacao, "O status")
        self._validar_conclusao(data_conclusao)
        filme = Filme(titulo, genero, ano, duracao_minutos, classificacao, elenco)
        self.catalogo.adicionar(filme)  # recusa duplicidade
        if status == StatusVisualizacao.ASSISTIDO:
            self.usuario.registrar_conclusao(filme, data_conclusao)
        else:
            filme.status = status
        return filme

    def adicionar_serie(
        self,
        titulo: str,
        genero: str,
        ano: int,
        classificacao: str,
        elenco: list[str] | None = None,
    ) -> Serie:
        """Cadastra uma serie (sem episodios; eles entram em adicionar_episodio)."""
        serie = Serie(titulo, genero, ano, classificacao, elenco)
        self.catalogo.adicionar(serie)
        return serie

    # ------------------------------------------------------------------
    # Episodios e status
    # ------------------------------------------------------------------
    def adicionar_episodio(
        self,
        serie_titulo: str,
        numero_temporada: int,
        numero_episodio: int,
        titulo: str,
        duracao_minutos: int,
        data_lancamento: date,
        ano_serie: int | None = None,
        status: StatusVisualizacao | str = StatusVisualizacao.NAO_ASSISTIDO,
        nota: float | None = None,
        quando: datetime | None = None,
    ) -> Episodio:
        """Adiciona um episodio na serie (cria a temporada se precisar).

        Adicionar episodio novo a uma serie ASSISTIDA a deixa ASSISTINDO de novo
        (e o registro dela sai do historico).

        Raises:
            ValueError: serie inexistente, dados invalidos, numero repetido ou
                nota em episodio que nao esta ASSISTIDO.
        """
        serie = self._resolver_serie(serie_titulo, ano_serie)
        status = validar_enum(status, StatusVisualizacao, "O status")
        self._validar_conclusao(quando)
        if nota is not None:
            validar_nota(nota)
            if status != StatusVisualizacao.ASSISTIDO:
                raise ValueError("So e possivel avaliar um episodio ja assistido.")
        episodio = Episodio(
            numero_temporada, numero_episodio, titulo, duracao_minutos, data_lancamento
        )
        serie.adicionar_episodio(episodio)
        if status != StatusVisualizacao.NAO_ASSISTIDO:
            serie.definir_status_episodio(
                numero_temporada, numero_episodio, status, quando
            )
        episodio.nota = nota
        self.usuario.sincronizar_historico(serie)
        return episodio

    def atualizar_status_serie(
        self,
        serie_titulo: str,
        status: StatusVisualizacao | str,
        numero_temporada: int | None = None,
        numero_episodio: int | None = None,
        todos: bool = False,
        ano_serie: int | None = None,
        quando: datetime | None = None,
    ) -> Serie:
        """Muda o status de um episodio (ou de todos) e recalcula o da serie.

        Quando todos os episodios ficam ASSISTIDO a serie vira ASSISTIDO e entra
        no historico; se algum deixar de estar, ela sai do historico.

        Raises:
            ValueError: serie/episodio inexistente, status invalido, data no
                futuro, ou nem 'todos' nem temporada+episodio informados.
        """
        serie = self._resolver_serie(serie_titulo, ano_serie)
        status = validar_enum(status, StatusVisualizacao, "O status")
        self._validar_conclusao(quando)
        if todos:
            if len(serie) == 0:
                raise ValueError("A serie ainda nao tem episodios.")
            alvos = [(e.numero_temporada, e.numero_episodio) for e in serie.todos_episodios()]
        elif numero_temporada is not None and numero_episodio is not None:
            alvos = [(numero_temporada, numero_episodio)]
        else:
            raise ValueError("Informe temporada e episodio, ou use todos.")
        for temporada, episodio in alvos:
            serie.definir_status_episodio(temporada, episodio, status, quando)
        self.usuario.sincronizar_historico(serie)
        return serie

    def atualizar_status_filme(
        self,
        titulo: str,
        status: StatusVisualizacao | str,
        ano: int | None = None,
        quando: datetime | None = None,
    ) -> Filme:
        """Muda o status de um filme (ASSISTIDO registra no historico).

        Raises:
            ValueError: se a midia nao for um filme ou ja estiver concluida.
        """
        midia = self.resolver_midia(titulo, TipoMidia.FILME, ano)
        status = validar_enum(status, StatusVisualizacao, "O status")
        if status == StatusVisualizacao.ASSISTIDO:
            self.concluir(titulo, TipoMidia.FILME, ano, quando)
        else:
            midia.status = status
            midia.data_conclusao = None
            self.usuario.sincronizar_historico(midia)
        assert isinstance(midia, Filme)
        return midia

    def concluir(
        self,
        titulo: str,
        tipo: TipoMidia | None = None,
        ano: int | None = None,
        quando: datetime | None = None,
    ) -> Midia:
        """Conclui uma midia (serie: os episodios que faltam) e registra no historico.

        Raises:
            ValueError: se ja estava concluida, data no futuro, ou serie sem episodios.
        """
        midia = self.resolver_midia(titulo, tipo, ano)
        self._validar_conclusao(quando)
        if midia.status == StatusVisualizacao.ASSISTIDO:
            raise ValueError(f"{midia.titulo!r} ja esta concluida.")
        self.usuario.registrar_conclusao(midia, quando)
        return midia

    # ------------------------------------------------------------------
    # Avaliacao
    # ------------------------------------------------------------------
    def avaliar(
        self,
        titulo: str,
        nota: float,
        tipo: TipoMidia | None = None,
        ano: int | None = None,
        numero_temporada: int | None = None,
        numero_episodio: int | None = None,
    ) -> Midia | Episodio:
        """Avalia um filme ou um episodio de serie (nota de 0 a 10).

        A nota da serie nao e dada diretamente: e a media dos episodios.

        Raises:
            ValueError: nota invalida, serie sem temporada/episodio, temporada/
                episodio em filme, ou item que ainda nao foi assistido.
        """
        validar_nota(nota)
        midia = self.resolver_midia(titulo, tipo, ano)
        if isinstance(midia, Serie):
            if numero_temporada is None or numero_episodio is None:
                raise ValueError(
                    "Series sao avaliadas por episodio: informe temporada e episodio."
                )
            alvo: Midia | Episodio = midia.obter_episodio(numero_temporada, numero_episodio)
        else:
            if numero_temporada is not None or numero_episodio is not None:
                raise ValueError("Temporada e episodio so valem para series.")
            alvo = midia
        if alvo.status != StatusVisualizacao.ASSISTIDO:
            raise ValueError("So e possivel avaliar o que ja foi assistido.")
        alvo.nota = nota
        return alvo

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def eh_recomendada(self, midia: Midia) -> bool:
        """True se a nota media da midia alcanca a nota minima do settings.json."""
        nota = midia.nota_media()
        return nota is not None and nota >= self.config.nota_minima_recomendado

    def listar(
        self,
        tipo: TipoMidia | None = None,
        genero: str | None = None,
        status: StatusVisualizacao | None = None,
        apenas_recomendadas: bool = False,
        por_nota: bool = False,
    ) -> list[Midia]:
        """Lista midias com filtros. Ordena por titulo, ou por nota (maior primeiro)."""
        midias = self.catalogo.midias
        if tipo is not None:
            midias = [m for m in midias if m.tipo == tipo]
        if genero is not None:
            midias = [m for m in midias if m.genero.lower() == genero.strip().lower()]
        if status is not None:
            midias = [m for m in midias if m.status == status]
        if apenas_recomendadas:
            midias = [m for m in midias if self.eh_recomendada(m)]
        if por_nota:
            return sorted(midias, reverse=True)  # usa o __lt__ da Midia
        return sorted(midias, key=lambda m: m.titulo.lower())

    # ------------------------------------------------------------------
    # Listas do usuario
    # ------------------------------------------------------------------
    def criar_lista(self, nome: str) -> ListaPersonalizada:
        """Cria uma lista personalizada (respeita o limite do settings.json)."""
        return self.usuario.criar_lista(nome)

    def adicionar_favorito(
        self,
        titulo: str,
        tipo: TipoMidia | None = None,
        ano: int | None = None,
        nome_lista: str = "Favoritos",
    ) -> Midia:
        """Poe a midia na lista (por padrao 'Favoritos'; cria a lista se faltar)."""
        midia = self.resolver_midia(titulo, tipo, ano)
        self.usuario.adicionar_favorito(midia, nome_lista)
        return midia

    def remover_da_lista(
        self,
        nome_lista: str,
        titulo: str,
        tipo: TipoMidia | None = None,
        ano: int | None = None,
    ) -> Midia:
        """Tira a midia de uma lista do usuario."""
        lista = self.usuario.obter_lista(nome_lista)
        midia = self.resolver_midia(titulo, tipo, ano)
        lista.remover(midia)
        return midia