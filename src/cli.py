"""CLI do catalogo de filmes e series.

Uso (a partir da raiz do projeto):

    python -m src.cli midia adicionar --titulo "Matrix" --tipo FILME ...
    python -m src.cli midia listar
    python -m src.cli --help
    python -m src.cli              (sem comando: abre o menu interativo)

Os dados ficam em dados/catalogo.json e dados/usuario.json. Na primeira
execucao o catalogo e criado com as midias do seed.

Cada comando le os argumentos, chama um metodo do Sistema (onde ficam as
regras de negocio) e salva. Erros de regra viram uma mensagem "Erro: ..." e
codigo de saida 1.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.serie import Serie
from src.services import relatorios
from src.services.sistema import Sistema

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS_PADRAO = RAIZ / "dados"
SETTINGS_PADRAO = RAIZ / "settings.json"

TIPOS = [t.value for t in TipoMidia]
STATUS = [s.name for s in StatusVisualizacao]  # NAO_ASSISTIDO, ASSISTINDO, ASSISTIDO


# ----------------------------------------------------------------------
# Conversores de argumentos
# ----------------------------------------------------------------------
def _data(texto: str) -> date:
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"data invalida: {texto!r} (use AAAA-MM-DD)") from None


def _data_hora(texto: str) -> datetime:
    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"data/hora invalida: {texto!r} (use AAAA-MM-DD ou AAAA-MM-DD HH:MM)"
        ) from None


def _tipo(texto: str | None) -> TipoMidia | None:
    return TipoMidia(texto) if texto else None


def _status(texto: str | None) -> StatusVisualizacao | None:
    return StatusVisualizacao[texto] if texto else None


def _elenco(texto: str | None) -> list[str]:
    if not texto:
        return []
    return [nome.strip() for nome in texto.split(",") if nome.strip()]


# ----------------------------------------------------------------------
# midia ...
# ----------------------------------------------------------------------
def cmd_midia_adicionar(sistema: Sistema, args: argparse.Namespace) -> None:
    elenco = _elenco(args.elenco)
    if args.tipo == TipoMidia.FILME.value:
        if args.duracao is None:
            raise ValueError("Filme precisa de --duracao (em minutos).")
        midia = sistema.adicionar_filme(
            args.titulo, args.genero, args.ano, args.duracao, args.classificacao,
            elenco, StatusVisualizacao[args.status], args.quando,
        )
    else:
        if args.duracao is not None:
            raise ValueError("Serie nao tem --duracao: ela vem da soma dos episodios.")
        if args.status != StatusVisualizacao.NAO_ASSISTIDO.name:
            raise ValueError(
                "O status da serie e calculado pelos episodios "
                "(use 'serie adicionar-episodio' / 'serie atualizar-status')."
            )
        midia = sistema.adicionar_serie(
            args.titulo, args.genero, args.ano, args.classificacao, elenco
        )
    sistema.salvar()
    print(f"Adicionado: {midia}")


def cmd_midia_avaliar(sistema: Sistema, args: argparse.Namespace) -> None:
    alvo = sistema.avaliar(
        args.titulo, args.nota, _tipo(args.tipo), args.ano, args.temporada, args.episodio
    )
    sistema.salvar()
    print(f"Avaliado com {args.nota:g}: {alvo}")
    midia = sistema.resolver_midia(args.titulo, _tipo(args.tipo), args.ano)
    if isinstance(midia, Serie):
        print(f"Nota media da serie: {midia.nota_media():.1f}")
    geral = sistema.catalogo.nota_geral()
    if geral is not None:
        print(f"Nota geral do catalogo: {geral:.1f}")


def cmd_midia_listar(sistema: Sistema, args: argparse.Namespace) -> None:
    midias = sistema.listar(
        _tipo(args.tipo), args.genero, _status(args.status), args.recomendadas, args.por_nota
    )
    if not midias:
        print("Nenhuma midia encontrada.")
        return
    for midia in midias:
        marca = "  * recomendado" if sistema.eh_recomendada(midia) else ""
        print(f"{midia}{marca}")
    print(f"\n{len(midias)} midia(s).")


def cmd_midia_detalhes(sistema: Sistema, args: argparse.Namespace) -> None:
    midia = sistema.resolver_midia(args.titulo, _tipo(args.tipo), args.ano)
    print(midia.detalhes())


def cmd_midia_concluir(sistema: Sistema, args: argparse.Namespace) -> None:
    midia = sistema.concluir(args.titulo, _tipo(args.tipo), args.ano, args.quando)
    sistema.salvar()
    print(f"Concluido em {midia.data_conclusao:%d/%m/%Y %H:%M}: {midia}")


def cmd_midia_atualizar_status(sistema: Sistema, args: argparse.Namespace) -> None:
    midia = sistema.resolver_midia(args.titulo, _tipo(args.tipo), args.ano)
    if isinstance(midia, Serie):
        raise ValueError("Para series use 'serie atualizar-status'.")
    filme = sistema.atualizar_status_filme(args.titulo, args.status, args.ano, args.quando)
    sistema.salvar()
    print(f"Status atualizado: {filme}")


# ----------------------------------------------------------------------
# midia relatorio ...
# ----------------------------------------------------------------------
def cmd_relatorio_top(sistema: Sistema, args: argparse.Namespace) -> None:
    melhores = relatorios.top_melhores(sistema.catalogo, args.limite)
    print(f"Top {args.limite} mais bem avaliados (so midias assistidas):")
    if not melhores:
        print("  (nenhuma)")
    for posicao, midia in enumerate(melhores, start=1):
        print(f"  {posicao}. {midia.titulo} ({midia.tipo.value}) - nota {midia.nota_media():.1f}")


def cmd_relatorio_generos(sistema: Sistema, args: argparse.Namespace) -> None:
    medias = relatorios.media_por_genero(sistema.catalogo)
    print("Nota media por genero (so midias assistidas):")
    if not medias:
        print("  (nenhuma)")
    for genero, nota in medias.items():
        print(f"  {genero}: {nota:.1f}")


def cmd_relatorio_tempo(sistema: Sistema, args: argparse.Namespace) -> None:
    print("Tempo total assistido por tipo:")
    for tipo, horas in relatorios.tempo_assistido_por_tipo(sistema.catalogo, sistema.config).items():
        print(f"  {tipo}: {horas} h")


def cmd_relatorio_series(sistema: Sistema, args: argparse.Namespace) -> None:
    series = relatorios.series_mais_assistidas(sistema.catalogo, args.limite)
    print("Series com mais episodios assistidos:")
    if not series:
        print("  (nenhuma)")
    for serie in series:
        print(f"  {serie.titulo}: {serie.episodios_assistidos()} de {len(serie)} episodios")


def cmd_relatorio_periodo(sistema: Sistema, args: argparse.Namespace) -> None:
    referencia = args.data or date.today()
    if args.semana:
        inicio, fim = relatorios.intervalo_semana(referencia)
        nome = "na semana"
    else:
        inicio, fim = relatorios.intervalo_mes(referencia)
        nome = "no mes"
    minutos = relatorios.minutos_assistidos_no_periodo(sistema.catalogo, inicio, fim)
    horas = sistema.config.minutos_para_horas(minutos)
    print(f"Tempo assistido {nome} ({inicio:%d/%m/%Y} a {fim:%d/%m/%Y}): {horas} h ({minutos} min)")


def cmd_relatorio_completo(sistema: Sistema, args: argparse.Namespace) -> None:
    print(relatorios.gerar_relatorio(sistema.catalogo, sistema.config, args.limite))


# ----------------------------------------------------------------------
# serie ...
# ----------------------------------------------------------------------
def cmd_serie_adicionar_episodio(sistema: Sistema, args: argparse.Namespace) -> None:
    episodio = sistema.adicionar_episodio(
        args.serie, args.temporada, args.episodio, args.titulo, args.duracao,
        args.lancamento, args.ano, StatusVisualizacao[args.status], args.nota, args.quando,
    )
    sistema.salvar()
    serie = sistema.resolver_midia(args.serie, TipoMidia.SERIE, args.ano)
    print(f"Episodio adicionado: {episodio}")
    print(f"Serie agora: {serie}")


def cmd_serie_atualizar_status(sistema: Sistema, args: argparse.Namespace) -> None:
    serie = sistema.atualizar_status_serie(
        args.serie, args.status, args.temporada, args.episodio, args.todos, args.ano, args.quando
    )
    sistema.salvar()
    print(f"Serie agora: {serie}")
    print(f"Episodios assistidos: {serie.episodios_assistidos()} de {len(serie)}")


def cmd_serie_episodios(sistema: Sistema, args: argparse.Namespace) -> None:
    serie = sistema.resolver_midia(args.serie, TipoMidia.SERIE, args.ano)
    assert isinstance(serie, Serie)
    print(serie.detalhes())
    for episodio in serie.todos_episodios():
        nota = f" - nota {episodio.nota:g}" if episodio.nota is not None else ""
        print(f"    {episodio}{nota}")


# ----------------------------------------------------------------------
# usuario ...
# ----------------------------------------------------------------------
def cmd_usuario_criar_lista(sistema: Sistema, args: argparse.Namespace) -> None:
    lista = sistema.criar_lista(args.nome)
    sistema.salvar()
    total = len(sistema.usuario.listas)
    limite = sistema.config.limite_listas_por_usuario
    print(f"Lista criada: {lista} ({total}/{limite} listas)")


def cmd_usuario_adicionar_favorito(sistema: Sistema, args: argparse.Namespace) -> None:
    midia = sistema.adicionar_favorito(args.titulo, _tipo(args.tipo), args.ano, args.lista)
    sistema.salvar()
    print(f"{midia.titulo!r} adicionado na lista {args.lista!r}.")


def cmd_usuario_remover(sistema: Sistema, args: argparse.Namespace) -> None:
    midia = sistema.remover_da_lista(args.lista, args.titulo, _tipo(args.tipo), args.ano)
    sistema.salvar()
    print(f"{midia.titulo!r} removido da lista {args.lista!r}.")


def cmd_usuario_listas(sistema: Sistema, args: argparse.Namespace) -> None:
    listas = sistema.usuario.listas
    if not listas:
        print("Nenhuma lista criada.")
    for lista in listas:
        print(lista)
        for midia in lista.midias:
            print(f"    - {midia.titulo} ({midia.ano}, {midia.tipo.value})")


def cmd_usuario_historico(sistema: Sistema, args: argparse.Namespace) -> None:
    historico = sorted(sistema.usuario.historico, key=lambda r: r.data_conclusao)
    if not historico:
        print("Historico vazio.")
    for registro in historico:
        print(registro)


# ----------------------------------------------------------------------
# seed
# ----------------------------------------------------------------------
def cmd_seed(sistema: Sistema, args: argparse.Namespace) -> None:
    if not args.forcar:
        raise ValueError("Isso apaga os dados atuais e recria o seed. Use --forcar pra confirmar.")
    Sistema.novo_com_seed(sistema.pasta_dados, sistema.config)
    print("Dados recriados com o seed.")


# ----------------------------------------------------------------------
# Montagem do parser
# ----------------------------------------------------------------------
def _identificar(parser: argparse.ArgumentParser, com_titulo: bool = True) -> None:
    """Argumentos que identificam uma midia: --titulo, --tipo, --ano."""
    if com_titulo:
        parser.add_argument("--titulo", required=True, help="titulo (ou pedaco dele)")
    parser.add_argument("--tipo", choices=TIPOS, help="FILME ou SERIE (se o titulo for ambiguo)")
    parser.add_argument("--ano", type=int, help="ano (se o titulo for ambiguo)")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.cli", description="Catalogo pessoal de filmes e series."
    )
    parser.add_argument("--dados", default=str(PASTA_DADOS_PADRAO), help="pasta dos arquivos JSON")
    parser.add_argument("--settings", default=str(SETTINGS_PADRAO), help="caminho do settings.json")
    grupos = parser.add_subparsers(dest="grupo", required=True, metavar="{midia,serie,usuario,seed}")

    # ---- midia ----
    midia = grupos.add_parser("midia", help="filmes e series do catalogo")
    sub = midia.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("adicionar", help="cadastra um filme ou uma serie")
    p.add_argument("--titulo", required=True)
    p.add_argument("--tipo", choices=TIPOS, required=True)
    p.add_argument("--genero", required=True)
    p.add_argument("--ano", type=int, required=True)
    p.add_argument("--duracao", type=int, help="minutos (so filme)")
    p.add_argument("--classificacao", required=True, help="L, 10, 12, 14, 16 ou 18")
    p.add_argument("--elenco", help='nomes separados por virgula: "Fulano, Ciclano"')
    p.add_argument("--status", choices=STATUS, default=StatusVisualizacao.NAO_ASSISTIDO.name)
    p.add_argument("--quando", type=_data_hora, help="data/hora da conclusao (se ja assistido)")
    p.set_defaults(func=cmd_midia_adicionar)

    p = sub.add_parser("avaliar", help="da nota (0 a 10) a um filme ou episodio")
    _identificar(p)
    p.add_argument("--nota", type=float, required=True)
    p.add_argument("--temporada", type=int, help="(series) numero da temporada")
    p.add_argument("--episodio", type=int, help="(series) numero do episodio")
    p.set_defaults(func=cmd_midia_avaliar)

    p = sub.add_parser("listar", help="lista as midias (com filtros)")
    _identificar(p, com_titulo=False)
    p.add_argument("--genero")
    p.add_argument("--status", choices=STATUS)
    p.add_argument("--recomendadas", action="store_true", help="so nota >= nota minima do settings.json")
    p.add_argument("--por-nota", action="store_true", help="ordena da maior pra menor nota")
    p.set_defaults(func=cmd_midia_listar)

    p = sub.add_parser("detalhes", help="mostra elenco, classificacao e temporadas")
    _identificar(p)
    p.set_defaults(func=cmd_midia_detalhes)

    p = sub.add_parser("concluir", help="marca como concluida e registra no historico")
    _identificar(p)
    p.add_argument("--quando", type=_data_hora, help="data/hora (padrao: agora)")
    p.set_defaults(func=cmd_midia_concluir)

    p = sub.add_parser("atualizar-status", help="muda o status de um filme")
    _identificar(p)
    p.add_argument("--status", choices=STATUS, required=True)
    p.add_argument("--quando", type=_data_hora)
    p.set_defaults(func=cmd_midia_atualizar_status)

    rel = sub.add_parser("relatorio", help="relatorios (so midias assistidas)")
    rsub = rel.add_subparsers(dest="relatorio", required=True)
    p = rsub.add_parser("top", help="top N mais bem avaliados")
    p.add_argument("--limite", type=int, default=10)
    p.set_defaults(func=cmd_relatorio_top)
    p = rsub.add_parser("generos", help="nota media por genero")
    p.set_defaults(func=cmd_relatorio_generos)
    p = rsub.add_parser("tempo", help="tempo total assistido por tipo")
    p.set_defaults(func=cmd_relatorio_tempo)
    p = rsub.add_parser("series", help="series com mais episodios assistidos")
    p.add_argument("--limite", type=int, default=10)
    p.set_defaults(func=cmd_relatorio_series)
    p = rsub.add_parser("periodo", help="tempo assistido na semana ou no mes")
    modo = p.add_mutually_exclusive_group(required=True)
    modo.add_argument("--semana", action="store_true")
    modo.add_argument("--mes", action="store_true")
    p.add_argument("--data", type=_data, help="dia de referencia (padrao: hoje)")
    p.set_defaults(func=cmd_relatorio_periodo)
    p = rsub.add_parser("completo", help="todos os relatorios juntos")
    p.add_argument("--limite", type=int, default=10)
    p.set_defaults(func=cmd_relatorio_completo)

    # ---- serie ----
    serie = grupos.add_parser("serie", help="temporadas e episodios")
    sub = serie.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("adicionar-episodio", help="adiciona um episodio a uma serie")
    p.add_argument("--serie", required=True, help="titulo da serie")
    p.add_argument("--ano", type=int, help="ano da serie (se o titulo for ambiguo)")
    p.add_argument("--temporada", type=int, required=True)
    p.add_argument("--episodio", type=int, required=True)
    p.add_argument("--titulo", required=True, help="titulo do episodio")
    p.add_argument("--duracao", type=int, required=True, help="minutos")
    p.add_argument("--lancamento", type=_data, required=True, help="AAAA-MM-DD")
    p.add_argument("--status", choices=STATUS, default=StatusVisualizacao.NAO_ASSISTIDO.name)
    p.add_argument("--nota", type=float, help="so se o episodio ja foi assistido")
    p.add_argument("--quando", type=_data_hora, help="data/hora em que foi assistido")
    p.set_defaults(func=cmd_serie_adicionar_episodio)

    p = sub.add_parser("atualizar-status", help="muda o status de episodio(s); a serie se ajusta sozinha")
    p.add_argument("--serie", required=True)
    p.add_argument("--ano", type=int)
    p.add_argument("--temporada", type=int)
    p.add_argument("--episodio", type=int)
    p.add_argument("--todos", action="store_true", help="aplica a todos os episodios")
    p.add_argument("--status", choices=STATUS, required=True)
    p.add_argument("--quando", type=_data_hora)
    p.set_defaults(func=cmd_serie_atualizar_status)

    p = sub.add_parser("episodios", help="lista os episodios de uma serie")
    p.add_argument("--serie", required=True)
    p.add_argument("--ano", type=int)
    p.set_defaults(func=cmd_serie_episodios)

    # ---- usuario ----
    usuario = grupos.add_parser("usuario", help="listas personalizadas e historico")
    sub = usuario.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("criar-lista", help="cria uma lista personalizada")
    p.add_argument("--nome", required=True)
    p.set_defaults(func=cmd_usuario_criar_lista)

    p = sub.add_parser("adicionar-favorito", help="poe uma midia numa lista (padrao: Favoritos)")
    _identificar(p)
    p.add_argument("--lista", default="Favoritos")
    p.set_defaults(func=cmd_usuario_adicionar_favorito)

    p = sub.add_parser("remover", help="tira uma midia de uma lista")
    _identificar(p)
    p.add_argument("--lista", required=True)
    p.set_defaults(func=cmd_usuario_remover)

    p = sub.add_parser("listas", help="mostra as listas e o que tem nelas")
    p.set_defaults(func=cmd_usuario_listas)

    p = sub.add_parser("historico", help="mostra o historico de conclusoes")
    p.set_defaults(func=cmd_usuario_historico)

    # ---- seed ----
    p = grupos.add_parser("seed", help="recria os dados de exemplo (apaga os atuais)")
    p.add_argument("--forcar", action="store_true")
    p.set_defaults(func=cmd_seed)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Executa um comando (ou abre o menu, se nao houver comando).

    Devolve 0 (ok) ou 1 (erro de regra/validacao).
    """
    argumentos = sys.argv[1:] if argv is None else argv
    if not argumentos:
        # sem nenhum comando: abre o menu interativo (src/menu.py)
        from src.menu import main as abrir_menu

        abrir_menu()
        return 0
    args = construir_parser().parse_args(argumentos)
    try:
        sistema = Sistema.abrir(args.dados, args.settings)
        args.func(sistema, args)
    except (ValueError, OSError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ----------------------------------------------------------------------
# COMO RODAR (na raiz do projeto)
# ----------------------------------------------------------------------
# Menu interativo (sem nenhum comando depois):
#   python -m src.cli
#   (digite o numero da opcao e siga as perguntas; 0 sai)
#
# Subcomandos:
#   python -m src.cli --help
#
#   python -m src.cli midia adicionar --titulo "Matrix" --tipo FILME --genero Ficcao --ano 1999 --duracao 136 --classificacao 14
#   python -m src.cli midia avaliar --titulo "Interestelar" --nota 9
#   python -m src.cli midia listar --por-nota
#   python -m src.cli midia relatorio top
#
#   python -m src.cli serie adicionar-episodio --serie "Dark" --temporada 1 --episodio 2 --titulo "Mentiras" --duracao 50 --lancamento 2017-12-08
#   python -m src.cli serie atualizar-status --serie "Dark" --temporada 1 --episodio 1 --status ASSISTIDO
#
#   python -m src.cli usuario criar-lista --nome "Maratona"
#   python -m src.cli usuario adicionar-favorito --titulo "Interestelar" --lista "Maratona"
#
# Outros relatorios:
#   python -m src.cli midia relatorio generos
#   python -m src.cli midia relatorio tempo
#   python -m src.cli midia relatorio completo
#
# Testes:
#   python -m pip install pytest
#   python -m pytest -v
#
# Na primeira execucao os dados de exemplo (seed) sao criados em dados/.
# Para recriar os dados: python -m src.cli seed --forcar