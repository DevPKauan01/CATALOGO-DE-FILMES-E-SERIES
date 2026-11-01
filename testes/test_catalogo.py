"""Testes do catalogo de filmes e series (rodar com: python -m pytest -v)."""

from datetime import date, datetime

import pytest

from src.config.configuracoes import Configuracoes
from src.models.enums import StatusVisualizacao as St
from src.models.enums import TipoMidia
from src.models.episodio import Episodio
from src.models.filme import Filme
from src.models.serie import Serie
from src.models.temporada import Temporada
from src.models.usuario import Usuario
from src.services import relatorios
from src.services.catalogo import Catalogo
from src.services.sistema import Sistema

LANC = date(2024, 1, 1)


@pytest.fixture
def sistema(tmp_path):
    config = Configuracoes()
    return Sistema(Catalogo(), Usuario("Teste", config), config, str(tmp_path))


def filme(titulo="Matrix", ano=1999, genero="Ficcao", minutos=120, **extra):
    return Filme(titulo, genero, ano, minutos, "14", **extra)


def serie_com_eps(n=2, minutos=40):
    serie = Serie("Dark", "Ficcao", 2017, "16")
    for i in range(1, n + 1):
        serie.adicionar_episodio(Episodio(1, i, f"Ep {i}", minutos, LANC))
    return serie


# ----------------------------- Filme / Midia -----------------------------
def test_filme_valido_tem_str_e_repr():
    f = filme()
    assert "Matrix" in str(f) and "1999" in str(f)
    assert "Filme" in repr(f)
    assert f.status == St.NAO_ASSISTIDO


def test_titulo_vazio_e_recusado():
    with pytest.raises(ValueError):
        filme(titulo="   ")


@pytest.mark.parametrize("minutos", [0, -5])
def test_duracao_deve_ser_positiva(minutos):
    with pytest.raises(ValueError):
        filme(minutos=minutos)


@pytest.mark.parametrize("nota", [-1, 10.5, 11, "abc"])
def test_nota_invalida_e_recusada(nota):
    with pytest.raises(ValueError):
        filme().nota = nota


def test_nota_nos_limites_e_aceita():
    f = filme()
    f.nota = 0
    f.nota = 10
    assert f.nota == 10


def test_classificacao_invalida_e_recusada():
    with pytest.raises(ValueError):
        Filme("X", "Drama", 2000, 90, "99")


def test_eq_compara_titulo_e_tipo():
    assert filme("Matrix") == filme("matrix", ano=2003)
    assert filme("Dark") != Serie("Dark", "Ficcao", 2017, "16")


def test_lt_ordena_por_nota_media():
    ruim, bom = filme("A", nota=3), filme("B", nota=9)
    assert ruim < bom
    assert sorted([bom, ruim]) == [ruim, bom]


def test_marcar_concluida_registra_data():
    f = filme()
    quando = datetime(2024, 5, 1, 20, 0)
    f.marcar_concluida(quando)
    assert f.status == St.ASSISTIDO and f.data_conclusao == quando


# ------------------------ Serie / Temporada / Episodio ------------------------
def test_episodio_numero_deve_ser_positivo():
    with pytest.raises(ValueError):
        Episodio(0, 1, "X", 40, LANC)
    with pytest.raises(ValueError):
        Episodio(1, 0, "X", 40, LANC)


def test_temporada_recusa_episodio_repetido_ou_de_outra_temporada():
    temp = Temporada(1)
    temp.adicionar_episodio(Episodio(1, 1, "A", 40, LANC))
    with pytest.raises(ValueError):
        temp.adicionar_episodio(Episodio(1, 1, "B", 40, LANC))
    with pytest.raises(ValueError):
        temp.adicionar_episodio(Episodio(2, 2, "C", 40, LANC))


def test_serie_len_e_duracao_somam_episodios():
    serie = serie_com_eps(n=3, minutos=40)
    assert len(serie) == 3
    assert serie.duracao_total() == 120


def test_status_da_serie_e_automatico():
    serie = serie_com_eps(n=2)
    assert serie.status == St.NAO_ASSISTIDO
    serie.definir_status_episodio(1, 1, St.ASSISTIDO)
    assert serie.status == St.ASSISTINDO
    serie.definir_status_episodio(1, 2, St.ASSISTIDO)
    assert serie.status == St.ASSISTIDO
    serie.definir_status_episodio(1, 2, St.NAO_ASSISTIDO)
    assert serie.status == St.ASSISTINDO


def test_nota_media_da_serie_ignora_episodios_sem_nota():
    serie = serie_com_eps(n=3)
    assert serie.nota_media() is None
    serie.obter_episodio(1, 1).nota = 8
    serie.obter_episodio(1, 2).nota = 10
    assert serie.nota_media() == 9


def test_obter_episodio_inexistente_da_erro():
    with pytest.raises(ValueError):
        serie_com_eps().obter_episodio(1, 99)


# --------------------------------- Catalogo ---------------------------------
def test_catalogo_recusa_duplicidade_de_titulo_tipo_e_ano():
    cat = Catalogo([filme("Matrix", 1999)])
    with pytest.raises(ValueError):
        cat.adicionar(filme("matrix", 1999))


def test_catalogo_aceita_mesmo_titulo_com_ano_ou_tipo_diferente():
    cat = Catalogo([filme("Matrix", 1999)])
    cat.adicionar(filme("Matrix", 2003))
    cat.adicionar(Serie("Matrix", "Ficcao", 1999, "14"))
    assert len(cat) == 3


def test_nota_geral_do_catalogo():
    cat = Catalogo()
    assert cat.nota_geral() is None
    a, b = filme("A", nota=6), filme("B", nota=10)
    a.marcar_concluida()
    b.marcar_concluida()
    cat.adicionar(a)
    cat.adicionar(b)
    assert cat.nota_geral() == 8


def test_nota_geral_ignora_midias_nao_concluidas():
    cat = Catalogo()
    feito = filme("A", nota=6)
    feito.marcar_concluida()
    cat.adicionar(feito)
    cat.adicionar(filme("B", nota=10))  # tem nota, mas nao esta ASSISTIDO
    serie = serie_com_eps(2)
    serie.definir_status_episodio(1, 1, St.ASSISTIDO)
    serie.obter_episodio(1, 1).nota = 10  # serie em andamento
    cat.adicionar(serie)
    assert cat.nota_geral() == 6


def test_buscar_ignora_maiusculas_e_pedacos():
    cat = Catalogo([filme("Interestelar", 2014)])
    assert len(cat.buscar("INTER")) == 1
    assert cat.buscar("xyz") == []


# --------------------------------- Sistema ---------------------------------
def test_filme_cadastrado_como_assistido_entra_no_historico(sistema):
    sistema.adicionar_filme(
        "Matrix", "Ficcao", 1999, 136, "14", [], St.ASSISTIDO, datetime(2024, 5, 1, 20, 0)
    )
    assert len(sistema.usuario.historico) == 1


def test_sistema_recusa_filme_duplicado(sistema):
    sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14")
    with pytest.raises(ValueError):
        sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14")


def test_avaliar_exige_midia_assistida(sistema):
    sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14")
    with pytest.raises(ValueError):
        sistema.avaliar("Matrix", 9)
    sistema.concluir("Matrix")
    sistema.avaliar("Matrix", 9)
    assert sistema.catalogo.nota_geral() == 9


def test_avaliar_recusa_nota_invalida(sistema):
    sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14", [], St.ASSISTIDO)
    for nota in (11, -1, "abc"):
        with pytest.raises(ValueError):
            sistema.avaliar("Matrix", nota)


def test_serie_so_e_avaliada_por_episodio(sistema):
    sistema.adicionar_serie("Dark", "Ficcao", 2017, "16")
    sistema.adicionar_episodio("Dark", 1, 1, "Piloto", 50, LANC)
    with pytest.raises(ValueError):
        sistema.avaliar("Dark", 8)
    sistema.atualizar_status_serie("Dark", St.ASSISTIDO, 1, 1)
    sistema.avaliar("Dark", 8, None, None, 1, 1)
    assert sistema.resolver_midia("Dark").nota_media() == 8


def test_serie_fica_assistida_ao_concluir_todos_os_episodios(sistema):
    sistema.adicionar_serie("Dark", "Ficcao", 2017, "16")
    sistema.adicionar_episodio("Dark", 1, 1, "A", 50, LANC)
    sistema.adicionar_episodio("Dark", 1, 2, "B", 50, LANC)
    serie = sistema.atualizar_status_serie("Dark", St.ASSISTIDO, todos=True)
    assert serie.status == St.ASSISTIDO
    assert len(sistema.usuario.historico) == 1


def test_episodio_novo_reabre_serie_assistida(sistema):
    sistema.adicionar_serie("Dark", "Ficcao", 2017, "16")
    sistema.adicionar_episodio("Dark", 1, 1, "A", 50, LANC)
    sistema.atualizar_status_serie("Dark", St.ASSISTIDO, todos=True)
    sistema.adicionar_episodio("Dark", 1, 2, "B", 50, LANC)
    assert sistema.resolver_midia("Dark").status == St.ASSISTINDO
    assert len(sistema.usuario.historico) == 0


def test_episodio_com_nota_exige_estar_assistido(sistema):
    sistema.adicionar_serie("Dark", "Ficcao", 2017, "16")
    with pytest.raises(ValueError):
        sistema.adicionar_episodio("Dark", 1, 1, "A", 50, LANC, nota=9)


def test_concluir_duas_vezes_da_erro(sistema):
    sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14")
    sistema.concluir("Matrix")
    with pytest.raises(ValueError):
        sistema.concluir("Matrix")


def test_conclusao_no_futuro_e_recusada(sistema):
    sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14")
    with pytest.raises(ValueError):
        sistema.concluir("Matrix", quando=datetime(2999, 1, 1))


def test_listar_filtra_e_ordena_por_nota(sistema):
    sistema.adicionar_filme("A", "Drama", 2000, 90, "L", [], St.ASSISTIDO)
    sistema.adicionar_filme("B", "Drama", 2001, 90, "L", [], St.ASSISTIDO)
    sistema.adicionar_filme("C", "Acao", 2002, 90, "L")
    sistema.avaliar("A", 6)
    sistema.avaliar("B", 9)
    assert [m.titulo for m in sistema.listar(genero="drama", por_nota=True)] == ["B", "A"]
    assert [m.titulo for m in sistema.listar(status=St.NAO_ASSISTIDO)] == ["C"]
    assert [m.titulo for m in sistema.listar(tipo=TipoMidia.SERIE)] == []


def test_recomendada_usa_nota_minima_das_configuracoes(sistema):
    sistema.adicionar_filme("A", "Drama", 2000, 90, "L", [], St.ASSISTIDO)
    sistema.adicionar_filme("B", "Drama", 2001, 90, "L", [], St.ASSISTIDO)
    sistema.avaliar("A", 7.4)
    sistema.avaliar("B", 7.5)
    assert not sistema.eh_recomendada(sistema.resolver_midia("A"))
    assert sistema.eh_recomendada(sistema.resolver_midia("B"))


# ------------------------------ Listas e favoritos ------------------------------
def test_limite_de_listas_das_configuracoes():
    usuario = Usuario("Teste", Configuracoes(limite_listas_por_usuario=2))
    usuario.criar_lista("A")
    usuario.criar_lista("B")
    with pytest.raises(ValueError):
        usuario.criar_lista("C")


def test_lista_com_nome_repetido_e_recusada(sistema):
    sistema.criar_lista("Maratona")
    with pytest.raises(ValueError):
        sistema.criar_lista("Maratona")


def test_favoritos_adicionar_e_remover(sistema):
    sistema.adicionar_filme("Matrix", "Ficcao", 1999, 136, "14")
    sistema.adicionar_favorito("Matrix")
    assert len(sistema.usuario.obter_lista("Favoritos").midias) == 1
    sistema.remover_da_lista("Favoritos", "Matrix")
    assert len(sistema.usuario.obter_lista("Favoritos").midias) == 0


# --------------------------------- Relatorios ---------------------------------
def montar_catalogo_assistido():
    cat = Catalogo()
    drama = filme("Drama1", 2000, "Drama", 60, nota=8)
    drama2 = filme("Drama2", 2001, "Drama", 60, nota=6)
    acao = filme("Acao1", 2002, "Acao", 120, nota=10)
    nao_visto = filme("Nao visto", 2003, "Acao", 500)
    for f in (drama, drama2, acao):
        f.marcar_concluida(datetime(2024, 5, 15, 10, 0))
    for f in (drama, drama2, acao, nao_visto):
        cat.adicionar(f)
    return cat


def test_media_por_genero_so_conta_midias_assistidas():
    assert relatorios.media_por_genero(montar_catalogo_assistido()) == {"Acao": 10, "Drama": 7}


def test_tempo_por_tipo_so_conta_assistidos_e_converte_em_horas():
    horas = relatorios.tempo_assistido_por_tipo(montar_catalogo_assistido(), Configuracoes())
    assert horas["FILME"] == 4.0 and horas["SERIE"] == 0


def test_top_vem_ordenado_e_respeita_o_limite():
    top = relatorios.top_melhores(montar_catalogo_assistido(), 2)
    assert [m.titulo for m in top] == ["Acao1", "Drama1"]


def test_series_mais_assistidas_ordena_por_episodios():
    cat = Catalogo()
    a, b = serie_com_eps(3), Serie("Outra", "Drama", 2020, "L")
    for i in (1, 2):
        b.adicionar_episodio(Episodio(1, i, f"E{i}", 30, LANC))
    a.definir_status_episodio(1, 1, St.ASSISTIDO)
    b.definir_status_episodio(1, 1, St.ASSISTIDO)
    b.definir_status_episodio(1, 2, St.ASSISTIDO)
    cat.adicionar(a)
    cat.adicionar(b)
    assert [s.titulo for s in relatorios.series_mais_assistidas(cat)] == ["Outra", "Dark"]


def test_tempo_assistido_por_semana_e_por_mes():
    cat = montar_catalogo_assistido()  # concluidos em 15/05/2024: 60 + 60 + 120 min
    ini, fim = relatorios.intervalo_semana(date(2024, 5, 15))
    assert relatorios.minutos_assistidos_no_periodo(cat, ini, fim) == 240
    ini, fim = relatorios.intervalo_semana(date(2024, 5, 22))
    assert relatorios.minutos_assistidos_no_periodo(cat, ini, fim) == 0
    ini, fim = relatorios.intervalo_mes(date(2024, 5, 31))
    assert relatorios.minutos_assistidos_no_periodo(cat, ini, fim) == 240


def test_conversao_minutos_para_horas_e_configuravel():
    assert Configuracoes().minutos_para_horas(90) == 1.5
    assert Configuracoes(casas_decimais_horas=0).minutos_para_horas(90) == 2
    with pytest.raises(ValueError):
        Configuracoes(multiplicador_duracao=0)


# --------------------------------- Persistencia ---------------------------------
def test_primeira_abertura_cria_o_seed(tmp_path):
    sistema = Sistema.abrir(str(tmp_path), str(tmp_path / "settings.json"))
    assert len(sistema.catalogo) > 0
    assert (tmp_path / "catalogo.json").exists()


def test_salvar_e_carregar_mantem_os_dados(tmp_path):
    caminho_settings = str(tmp_path / "settings.json")
    sistema = Sistema.abrir(str(tmp_path), caminho_settings)
    sistema.adicionar_serie("Serie Nova", "Drama", 2023, "12")
    sistema.adicionar_episodio("Serie Nova", 1, 1, "Piloto", 45, LANC, status=St.ASSISTIDO, nota=9)
    sistema.criar_lista("Minha lista")
    sistema.salvar()

    reaberto = Sistema.abrir(str(tmp_path), caminho_settings)
    serie = reaberto.resolver_midia("Serie Nova")
    assert len(serie) == 1 and serie.nota_media() == 9 and serie.status == St.ASSISTIDO
    assert reaberto.usuario.obter_lista("Minha lista") is not None