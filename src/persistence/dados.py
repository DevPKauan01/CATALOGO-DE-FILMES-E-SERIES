"""Salvar/carregar o catalogo em JSON (json.dump / json.load) e seed.

A conversao objeto <-> dict fica nas proprias classes (para_dict/de_dict);
aqui so cuidamos de ler e gravar o arquivo e de ligar as referencias.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime

from src.config.configuracoes import Configuracoes
from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.episodio import Episodio
from src.models.filme import Filme
from src.models.midia import Midia
from src.models.registro_historico import RegistroHistorico
from src.models.serie import Serie
from src.models.usuario import Usuario
from src.services.catalogo import Catalogo
from src.utils.validacoes import validar_enum

# Qual classe reconstroi cada tipo de midia
_CLASSES = {TipoMidia.FILME: Filme, TipoMidia.SERIE: Serie}


def _gravar_json(dados: dict, caminho: str) -> None:
    """Grava o dict no arquivo (cria a pasta se nao existir)."""
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def _ler_json(caminho: str) -> dict:
    """Le o arquivo JSON e devolve o dict."""
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _referencia(midia: Midia) -> dict[str, object]:
    """Identifica uma midia (titulo + tipo + ano) sem copiar ela inteira."""
    return {"titulo": midia.titulo, "tipo": midia.tipo.value, "ano": midia.ano}


def _buscar_no_catalogo(catalogo: Catalogo, referencia: dict) -> Midia:
    """Acha no catalogo a midia citada na referencia."""
    tipo = validar_enum(referencia["tipo"], TipoMidia, "O tipo")
    midia = catalogo.obter(referencia["titulo"], tipo, referencia["ano"])
    if midia is None:
        raise ValueError(
            f"Midia {referencia['titulo']!r} ({referencia['ano']}) "
            "nao encontrada no catalogo."
        )
    return midia


def salvar_catalogo(catalogo: Catalogo, caminho: str) -> None:
    """Grava as midias (com temporadas e episodios) no arquivo."""
    # Cada midia sabe se converter (Filme e Serie sobrescrevem o para_dict)
    dados = {"midias": [midia.para_dict() for midia in catalogo.midias]}
    _gravar_json(dados, caminho)


def carregar_catalogo(caminho: str) -> Catalogo:
    """Le o arquivo e reconstroi o Catalogo com seus objetos."""
    dados = _ler_json(caminho)
    catalogo = Catalogo()
    for item in dados["midias"]:
        tipo = validar_enum(item["tipo"], TipoMidia, "O tipo")
        catalogo.adicionar(_CLASSES[tipo].de_dict(item))
    return catalogo


def salvar_usuario(usuario: Usuario, caminho: str) -> None:
    """Grava o usuario, suas listas e o historico.

    As listas e o historico guardam so a referencia das midias; as midias
    em si ficam no arquivo do catalogo.
    """
    dados = {
        "nome": usuario.nome,
        "listas": [
            {"nome": lista.nome, "midias": [_referencia(m) for m in lista.midias]}
            for lista in usuario.listas
        ],
        "historico": [
            {
                **_referencia(registro.midia),
                "data_conclusao": registro.data_conclusao.isoformat(),
            }
            for registro in usuario.historico
        ],
    }
    _gravar_json(dados, caminho)


def carregar_usuario(
    caminho: str,
    catalogo: Catalogo,
    configuracoes: Configuracoes | None = None,
) -> Usuario:
    """Le o usuario e liga as listas/historico as midias do catalogo.

    Raises:
        ValueError: se uma lista ou o historico citar uma midia que nao
            existe no catalogo.
    """
    dados = _ler_json(caminho)
    usuario = Usuario(dados["nome"], configuracoes)
    for item in dados.get("listas", []):
        lista = usuario.criar_lista(item["nome"])
        for referencia in item.get("midias", []):
            lista.adicionar(_buscar_no_catalogo(catalogo, referencia))
    for item in dados.get("historico", []):
        midia = _buscar_no_catalogo(catalogo, item)
        quando = datetime.fromisoformat(item["data_conclusao"])
        usuario.historico.append(RegistroHistorico(midia, quando))
    return usuario


def seed() -> Catalogo:
    """Cria um catalogo com filmes e series pre-cadastrados."""
    catalogo = Catalogo()

    interestelar = Filme(
        "Interestelar", "Ficcao", 2014, 169, "10",
        elenco=["Matthew McConaughey", "Anne Hathaway"],
    )
    interestelar.nota = 9.5
    interestelar.marcar_concluida(datetime(2026, 9, 10, 21, 0))
    catalogo.adicionar(interestelar)

    cidade_de_deus = Filme(
        "Cidade de Deus", "Drama", 2002, 130, "18",
        elenco=["Alexandre Rodrigues", "Leandro Firmino"],
    )
    cidade_de_deus.nota = 9.0
    cidade_de_deus.marcar_concluida(datetime(2026, 9, 20, 20, 30))
    catalogo.adicionar(cidade_de_deus)

    catalogo.adicionar(Filme("Parasita", "Suspense", 2019, 132, "16"))

    breaking_bad = Serie("Breaking Bad", "Drama", 2008, "16", elenco=["Bryan Cranston"])
    for numero, titulo, minutos in [(1, "Pilot", 58), (2, "Cat's in the Bag", 48)]:
        episodio = Episodio(1, numero, titulo, minutos, date(2008, 1, 20))
        episodio.nota = 9.0
        episodio.marcar_assistido(datetime(2026, 10, numero))
        breaking_bad.adicionar_episodio(episodio)
    breaking_bad.adicionar_episodio(Episodio(1, 3, "...And the Bag's in the River", 48, date(2008, 2, 10)))
    catalogo.adicionar(breaking_bad)

    dark = Serie("Dark", "Ficcao", 2017, "16")
    dark.adicionar_episodio(Episodio(1, 1, "Segredos", 50, date(2017, 12, 1)))
    catalogo.adicionar(dark)

    return catalogo


def seed_usuario(
    catalogo: Catalogo, configuracoes: Configuracoes | None = None
) -> Usuario:
    """Cria o usuario padrao com listas e historico coerentes com o seed."""
    usuario = Usuario("Usuario", configuracoes)
    for midia in catalogo.concluidas():
        usuario.sincronizar_historico(midia)
    favoritos = usuario.criar_lista("Favoritos")
    para_assistir = usuario.criar_lista("Para assistir")
    for midia in catalogo.midias:
        if midia.titulo == "Interestelar":
            favoritos.adicionar(midia)
        if midia.titulo in ("Parasita", "Dark"):
            para_assistir.adicionar(midia)
    return usuario
