"""Salvar/carregar o catalogo em JSON (ou SQLite)."""

from __future__ import annotations

from src.catalogo import Catalogo
from src.models.usuario import Usuario


def salvar_catalogo(catalogo: Catalogo, caminho: str) -> None:
    """Grava as midias (com temporadas e episodios) no arquivo."""
    raise NotImplementedError


def carregar_catalogo(caminho: str) -> Catalogo:
    """Le o arquivo e reconstroi o Catalogo com seus objetos."""
    raise NotImplementedError


def salvar_usuario(usuario: Usuario, caminho: str) -> None:
    """Grava o usuario, suas listas e o historico."""
    raise NotImplementedError


def carregar_usuario(caminho: str, catalogo: Catalogo) -> Usuario:
    """Le o usuario e liga as listas/historico as midias do catalogo."""
    raise NotImplementedError


def seed() -> Catalogo:
    """Cria um catalogo com filmes e series pre-cadastrados."""
    raise NotImplementedError
