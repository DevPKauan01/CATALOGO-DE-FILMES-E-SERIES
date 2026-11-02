"""Relatorios do catalogo. Consideram so midias ASSISTIDO."""

from __future__ import annotations

import calendar
from datetime import date, datetime, time, timedelta

from src.services.catalogo import Catalogo
from src.config.configuracoes import Configuracoes
from src.models.enums import TipoMidia
from src.models.midia import Midia
from src.models.serie import Serie


def media_por_genero(catalogo: Catalogo) -> dict[str, float]:
    """Nota media por genero (so midias concluidas e com nota)."""
    notas_por_genero: dict[str, list[float]] = {}
    for midia in catalogo.concluidas():
        nota = midia.nota_media()
        if nota is not None:
            notas_por_genero.setdefault(midia.genero, []).append(nota)
    return {
        genero: round(sum(notas) / len(notas), 2)
        for genero, notas in sorted(notas_por_genero.items())
    }


def tempo_assistido_por_tipo(
    catalogo: Catalogo, config: Configuracoes
) -> dict[str, float]:
    """Tempo total assistido (em horas) por tipo: FILME e SERIE."""
    minutos = {tipo.value: 0 for tipo in TipoMidia}
    for midia in catalogo.concluidas():
        minutos[midia.tipo.value] += midia.duracao_total()
    return {tipo: config.minutos_para_horas(m) for tipo, m in minutos.items()}


def top_melhores(catalogo: Catalogo, limite: int = 10) -> list[Midia]:
    """Top N filmes/series mais bem avaliados (so concluidos e com nota)."""
    avaliadas = [m for m in catalogo.concluidas() if m.nota_media() is not None]
    # sorted usa o __lt__ da Midia (compara pela nota media)
    return sorted(avaliadas, reverse=True)[:limite]


def series_mais_assistidas(catalogo: Catalogo, limite: int = 10) -> list[Serie]:
    """Series com maior numero de episodios assistidos.

    Aqui entram tambem as series ASSISTINDO (em andamento), senao uma serie
    pela metade nunca apareceria no ranking.
    """
    series = [
        m for m in catalogo.midias
        if isinstance(m, Serie) and m.episodios_assistidos() > 0
    ]
    series.sort(key=lambda s: s.episodios_assistidos(), reverse=True)
    return series[:limite]


def tempo_assistido_no_periodo(
    catalogo: Catalogo,
    inicio: datetime,
    fim: datetime,
    config: Configuracoes,
) -> float:
    """Tempo total assistido (em horas) entre duas datas (semana/mes).

    Cada midia calcula o seu (Filme pela data de conclusao, Serie episodio
    por episodio), por isso aqui nao precisa de if pra cada tipo.
    """
    minutos = sum(
        midia.minutos_assistidos_no_periodo(inicio, fim) for midia in catalogo.midias
    )
    return config.minutos_para_horas(minutos)


def minutos_assistidos_no_periodo(
    catalogo: Catalogo, inicio: datetime, fim: datetime
) -> int:
    """Minutos assistidos entre duas datas (cada midia calcula o seu)."""
    return sum(
        midia.minutos_assistidos_no_periodo(inicio, fim) for midia in catalogo.midias
    )


def intervalo_semana(referencia: date) -> tuple[datetime, datetime]:
    """Inicio (segunda 00:00) e fim (domingo 23:59:59) da semana da data."""
    segunda = referencia - timedelta(days=referencia.weekday())
    domingo = segunda + timedelta(days=6)
    return datetime.combine(segunda, time.min), datetime.combine(domingo, time.max)


def intervalo_mes(referencia: date) -> tuple[datetime, datetime]:
    """Inicio (dia 1, 00:00) e fim (ultimo dia, 23:59:59) do mes da data."""
    ultimo_dia = calendar.monthrange(referencia.year, referencia.month)[1]
    primeiro = referencia.replace(day=1)
    ultimo = referencia.replace(day=ultimo_dia)
    return datetime.combine(primeiro, time.min), datetime.combine(ultimo, time.max)


def gerar_relatorio(
    catalogo: Catalogo, config: Configuracoes, limite: int = 5
) -> str:
    """Junta os relatorios acima num texto simples pra imprimir."""
    nota_geral = catalogo.nota_geral()
    linhas = [
        "===== RELATORIO DO CATALOGO =====",
        f"Midias cadastradas: {len(catalogo)} | concluidas: {len(catalogo.concluidas())}",
        "Nota media geral: "
        + (f"{nota_geral:.1f}" if nota_geral is not None else "sem notas"),
        "",
        "Nota media por genero:",
    ]
    medias = media_por_genero(catalogo)
    linhas += [f"  {g}: {n:.1f}" for g, n in medias.items()] or ["  (nenhuma)"]

    linhas += ["", "Tempo assistido:"]
    for tipo, horas in tempo_assistido_por_tipo(catalogo, config).items():
        linhas.append(f"  {tipo}: {horas} h")

    linhas += ["", f"Top {limite} melhores:"]
    melhores = top_melhores(catalogo, limite)
    linhas += [
        f"  {i}. {m.titulo} - nota {m.nota_media():.1f}"
        for i, m in enumerate(melhores, start=1)
    ] or ["  (nenhuma)"]

    linhas += ["", "Series mais assistidas:"]
    series = series_mais_assistidas(catalogo, limite)
    linhas += [
        f"  {s.titulo}: {s.episodios_assistidos()} de {len(s)} episodios"
        for s in series
    ] or ["  (nenhuma)"]
    return "\n".join(linhas)
