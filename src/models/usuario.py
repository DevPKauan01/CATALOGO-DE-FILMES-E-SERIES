"""Usuario - dono das listas e do historico."""

from __future__ import annotations

from src.config.configuracoes import Configuracoes
from src.models.lista_personalizada import ListaPersonalizada
from src.models.midia import Midia
from src.models.registro_historico import RegistroHistorico
from src.utils.validacoes import validar_texto


class Usuario:
    """Usuario do catalogo (composicao: possui listas e historico).

    Relacionamentos:
        - composicao com ListaPersonalizada (0..* listas);
        - composicao com RegistroHistorico (0..* registros);
        - associacao com Configuracoes (usa o limite de listas).

    Atributos:
        nome: nome do usuario (nao pode ser vazio).
        configuracoes: configuracoes do sistema (usadas pro limite de listas).
        listas: listas personalizadas do usuario.
        historico: registros de conclusao de midias.
    """

    def __init__(self, nome: str, configuracoes: Configuracoes | None = None) -> None:
        self.nome = nome
        self.configuracoes = configuracoes if configuracoes is not None else Configuracoes()
        self.listas: list[ListaPersonalizada] = []
        self.historico: list[RegistroHistorico] = []

    @property
    def nome(self) -> str:
        """Nome do usuario (nao pode ser vazio)."""
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        self._nome = validar_texto(valor, "O nome do usuario")

    def _buscar_lista(self, nome: str) -> ListaPersonalizada | None:
        """Procura uma lista pelo nome, sem diferenciar maiuscula (None se nao achar)."""
        for lista in self.listas:
            if lista.nome.lower() == nome.strip().lower():
                return lista
        return None

    def criar_lista(self, nome: str) -> ListaPersonalizada:
        """Cria uma lista nova respeitando o limite do settings.json.

        Raises:
            ValueError: se o limite foi atingido, o nome for vazio ou ja existir.
        """
        limite = self.configuracoes.limite_listas_por_usuario
        if len(self.listas) >= limite:
            raise ValueError(f"Limite de {limite} listas por usuario atingido.")
        lista = ListaPersonalizada(nome)  # valida o nome
        if self._buscar_lista(lista.nome) is not None:
            raise ValueError(f"Ja existe uma lista chamada {lista.nome!r}.")
        self.listas.append(lista)
        return lista

    def obter_lista(self, nome: str) -> ListaPersonalizada:
        """Busca uma lista do usuario pelo nome.

        Raises:
            ValueError: se nao existir lista com esse nome.
        """
        lista = self._buscar_lista(nome)
        if lista is None:
            raise ValueError(f"Nao existe a lista {nome!r}.")
        return lista

    def adicionar_favorito(self, midia: Midia, nome_lista: str = "Favoritos") -> None:
        """Adiciona a midia na lista de favoritos (ou outra lista informada).

        Se a lista ainda nao existir, ela e criada.
        """
        lista = self._buscar_lista(nome_lista)
        if lista is None:
            lista = self.criar_lista(nome_lista)
        lista.adicionar(midia)

    def registrar_conclusao(self, midia: Midia) -> None:
        """Marca a midia como concluida e cria o registro no historico.

        Raises:
            ValueError: se a midia ja estiver no historico (evita sobrescrever
                a data da conclusao anterior).
        """
        if any(registro.midia == midia for registro in self.historico):
            raise ValueError(f"{midia.titulo!r} ja esta no historico.")
        midia.marcar_concluida()
        self.historico.append(RegistroHistorico(midia, midia.data_conclusao))
