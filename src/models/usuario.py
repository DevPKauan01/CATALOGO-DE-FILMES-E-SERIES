"""Usuario - dono das listas e do historico."""

from __future__ import annotations

from src.config.configuracoes import Configuracoes
from src.models.lista_personalizada import ListaPersonalizada
from src.models.midia import Midia
from src.models.registro_historico import RegistroHistorico


class Usuario:
    """Usuario do catalogo (composicao: possui listas e historico).

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

    def criar_lista(self, nome: str) -> ListaPersonalizada:
        """Cria uma lista nova respeitando o limite do settings.json."""
        raise NotImplementedError

    def obter_lista(self, nome: str) -> ListaPersonalizada:
        """Busca uma lista do usuario pelo nome."""
        raise NotImplementedError

    def adicionar_favorito(self, midia: Midia, nome_lista: str = "Favoritos") -> None:
        """Adiciona a midia na lista de favoritos (ou outra lista informada)."""
        raise NotImplementedError

    def registrar_conclusao(self, midia: Midia) -> None:
        """Marca a midia como concluida e cria o registro no historico."""
        raise NotImplementedError
