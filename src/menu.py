"""Menu interativo do catalogo de filmes e series.

Rodar (na raiz do projeto):

    python -m src.menu

Funciona com a CLI antiga (src/cli.py) ou com a nova (src/cli/): este arquivo
nao depende de nenhuma das duas, so do Sistema.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.serie import Serie
from src.services import relatorios
from src.services.sistema import Sistema

RAIZ = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# Funcoes de perguntar (leem o que a pessoa digita)
# ----------------------------------------------------------------------
def perguntar(texto: str, obrigatorio: bool = True) -> str:
    while True:
        resposta = input(f"{texto}: ").strip()
        if resposta or not obrigatorio:
            return resposta
        print("  Isso nao pode ficar vazio.")


def perguntar_int(texto: str, obrigatorio: bool = True) -> int | None:
    while True:
        resposta = perguntar(texto, obrigatorio)
        if not resposta:
            return None
        try:
            return int(resposta)
        except ValueError:
            print("  Digite um numero inteiro.")


def perguntar_nota(texto: str = "Nota (0 a 10)") -> float:
    while True:
        resposta = perguntar(texto).replace(",", ".")
        try:
            return float(resposta)
        except ValueError:
            print("  Digite um numero, por exemplo 8.5")


def perguntar_data(texto: str) -> date:
    while True:
        resposta = perguntar(f"{texto} (AAAA-MM-DD)")
        try:
            return date.fromisoformat(resposta)
        except ValueError:
            print("  Data invalida. Exemplo: 2024-05-31")


def perguntar_sim_nao(texto: str) -> bool:
    return perguntar(f"{texto} (s/n)").lower().startswith("s")


def perguntar_elenco() -> list[str]:
    texto = perguntar("Elenco, separado por virgula (Enter pra pular)", obrigatorio=False)
    return [nome.strip() for nome in texto.split(",") if nome.strip()]


def perguntar_status() -> StatusVisualizacao:
    print("  1) Nao assistido   2) Assistindo   3) Assistido")
    opcoes = {
        "1": StatusVisualizacao.NAO_ASSISTIDO,
        "2": StatusVisualizacao.ASSISTINDO,
        "3": StatusVisualizacao.ASSISTIDO,
    }
    while True:
        escolha = perguntar("Status")
        if escolha in opcoes:
            return opcoes[escolha]
        print("  Escolha 1, 2 ou 3.")


def perguntar_midia() -> tuple[str, int | None]:
    """Pergunta o titulo e, se precisar, o ano (pra diferenciar titulos iguais)."""
    titulo = perguntar("Titulo (ou pedaco dele)")
    ano = perguntar_int("Ano (Enter pra pular)", obrigatorio=False)
    return titulo, ano


# ----------------------------------------------------------------------
# Opcoes do menu
# ----------------------------------------------------------------------
def listar(sistema: Sistema) -> None:
    midias = sistema.listar(None, None, None, False, False)
    if not midias:
        print("Nenhuma midia cadastrada.")
        return
    for midia in midias:
        marca = "  * recomendado" if sistema.eh_recomendada(midia) else ""
        print(f"{midia}{marca}")
    print(f"\n{len(midias)} midia(s).")


def detalhes(sistema: Sistema) -> None:
    titulo, ano = perguntar_midia()
    print(sistema.resolver_midia(titulo, None, ano).detalhes())


def adicionar_filme(sistema: Sistema) -> None:
    titulo = perguntar("Titulo")
    genero = perguntar("Genero")
    ano = perguntar_int("Ano")
    duracao = perguntar_int("Duracao em minutos")
    classificacao = perguntar("Classificacao (L, 10, 12, 14, 16 ou 18)")
    elenco = perguntar_elenco()
    filme = sistema.adicionar_filme(
        titulo, genero, ano, duracao, classificacao, elenco,
        StatusVisualizacao.NAO_ASSISTIDO, None,
    )
    sistema.salvar()
    print(f"Adicionado: {filme}")


def adicionar_serie(sistema: Sistema) -> None:
    titulo = perguntar("Titulo")
    genero = perguntar("Genero")
    ano = perguntar_int("Ano")
    classificacao = perguntar("Classificacao (L, 10, 12, 14, 16 ou 18)")
    elenco = perguntar_elenco()
    serie = sistema.adicionar_serie(titulo, genero, ano, classificacao, elenco)
    sistema.salvar()
    print(f"Adicionada: {serie}")


def adicionar_episodio(sistema: Sistema) -> None:
    nome_serie = perguntar("Titulo da serie")
    ano_serie = perguntar_int("Ano da serie (Enter pra pular)", obrigatorio=False)
    temporada = perguntar_int("Numero da temporada")
    episodio = perguntar_int("Numero do episodio")
    titulo = perguntar("Titulo do episodio")
    duracao = perguntar_int("Duracao em minutos")
    lancamento = perguntar_data("Data de lancamento")
    ep = sistema.adicionar_episodio(
        nome_serie, temporada, episodio, titulo, duracao, lancamento, ano_serie,
        StatusVisualizacao.NAO_ASSISTIDO, None, None,
    )
    sistema.salvar()
    print(f"Episodio adicionado: {ep}")


def avaliar(sistema: Sistema) -> None:
    titulo, ano = perguntar_midia()
    midia = sistema.resolver_midia(titulo, None, ano)
    temporada = episodio = None
    if isinstance(midia, Serie):
        print("Serie: a nota vai pra um episodio.")
        temporada = perguntar_int("Numero da temporada")
        episodio = perguntar_int("Numero do episodio")
    nota = perguntar_nota()
    alvo = sistema.avaliar(titulo, nota, None, ano, temporada, episodio)
    sistema.salvar()
    print(f"Avaliado com {nota:g}: {alvo}")


def concluir(sistema: Sistema) -> None:
    titulo, ano = perguntar_midia()
    midia = sistema.concluir(titulo, None, ano, None)
    sistema.salvar()
    print(f"Concluido em {midia.data_conclusao:%d/%m/%Y %H:%M}: {midia}")


def atualizar_status(sistema: Sistema) -> None:
    titulo, ano = perguntar_midia()
    midia = sistema.resolver_midia(titulo, None, ano)
    if isinstance(midia, Serie):
        todos = perguntar_sim_nao("Aplicar a todos os episodios")
        temporada = episodio = None
        if not todos:
            temporada = perguntar_int("Numero da temporada")
            episodio = perguntar_int("Numero do episodio")
        status = perguntar_status()
        serie = sistema.atualizar_status_serie(titulo, status, temporada, episodio, todos, ano, None)
        sistema.salvar()
        print(f"Serie agora: {serie}")
        print(f"Episodios assistidos: {serie.episodios_assistidos()} de {len(serie)}")
    else:
        status = perguntar_status()
        filme = sistema.atualizar_status_filme(titulo, status, ano, None)
        sistema.salvar()
        print(f"Status atualizado: {filme}")


def top_melhores(sistema: Sistema) -> None:
    limite = perguntar_int("Quantas midias mostrar (Enter = 10)", obrigatorio=False) or 10
    melhores = relatorios.top_melhores(sistema.catalogo, limite)
    print(f"Top {limite} mais bem avaliados (so midias assistidas):")
    if not melhores:
        print("  (nenhuma)")
    for posicao, midia in enumerate(melhores, start=1):
        print(f"  {posicao}. {midia.titulo} ({midia.tipo.value}) - nota {midia.nota_media():.1f}")


def mostrar_listas(sistema: Sistema) -> None:
    listas = sistema.usuario.listas
    if not listas:
        print("Nenhuma lista criada.")
    for lista in listas:
        print(lista)
        for midia in lista.midias:
            print(f"    - {midia.titulo} ({midia.ano}, {midia.tipo.value})")


def criar_lista(sistema: Sistema) -> None:
    lista = sistema.criar_lista(perguntar("Nome da lista"))
    sistema.salvar()
    print(f"Lista criada: {lista}")


def adicionar_favorito(sistema: Sistema) -> None:
    titulo, ano = perguntar_midia()
    nome_lista = perguntar("Nome da lista (Enter = Favoritos)", obrigatorio=False) or "Favoritos"
    midia = sistema.adicionar_favorito(titulo, None, ano, nome_lista)
    sistema.salvar()
    print(f"{midia.titulo!r} adicionado na lista {nome_lista!r}.")


def mostrar_historico(sistema: Sistema) -> None:
    historico = sorted(sistema.usuario.historico, key=lambda r: r.data_conclusao)
    if not historico:
        print("Historico vazio.")
    for registro in historico:
        print(registro)


def relatorio_completo(sistema: Sistema) -> None:
    print(relatorios.gerar_relatorio(sistema.catalogo, sistema.config, 10))


# (texto do menu, funcao). A ordem aqui e a ordem na tela.
OPCOES = [
    ("Listar midias", listar),
    ("Ver detalhes de uma midia", detalhes),
    ("Adicionar filme", adicionar_filme),
    ("Adicionar serie", adicionar_serie),
    ("Adicionar episodio a uma serie", adicionar_episodio),
    ("Avaliar (dar nota)", avaliar),
    ("Marcar como concluido", concluir),
    ("Atualizar status (filme ou episodios de serie)", atualizar_status),
    ("Ver minhas listas", mostrar_listas),
    ("Criar lista", criar_lista),
    ("Colocar midia numa lista (favoritos)", adicionar_favorito),
    ("Ver historico", mostrar_historico),
    ("Top mais bem avaliados", top_melhores),
    ("Relatorio completo", relatorio_completo),
]


def mostrar_menu() -> None:
    print("\n===== CATALOGO DE FILMES E SERIES =====")
    for numero, (texto, _) in enumerate(OPCOES, start=1):
        print(f"{numero:>2}) {texto}")
    print(" 0) Sair")


def main() -> None:
    try:
        sistema = Sistema.abrir(str(RAIZ / "dados"), str(RAIZ / "settings.json"))
    except (ValueError, OSError) as erro:
        print(f"Erro ao abrir os dados: {erro}")
        print("Dica: se os arquivos de dados/ estiverem vazios, apague os .json de la e rode de novo.")
        return

    while True:
        mostrar_menu()
        try:
            escolha = input("\nEscolha uma opcao: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAte mais!")
            return
        if escolha == "0":
            print("Ate mais!")
            return
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(OPCOES):
            print("Opcao invalida.")
            continue
        _, funcao = OPCOES[int(escolha) - 1]
        print()
        try:
            funcao(sistema)
        except (ValueError, OSError) as erro:
            print(f"Erro: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\n(cancelado)")


if __name__ == "__main__":
    main()