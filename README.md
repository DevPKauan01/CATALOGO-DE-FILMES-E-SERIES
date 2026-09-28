# Catálogo de Filmes e Séries

Projeto 1 de POO (UFCA - Eng. de Software) - Tema 10.

## Sobre o projeto

A ideia é um CLI pra gerenciar um catálogo pessoal de filmes e séries.
Dá pra cadastrar mídias, acompanhar temporadas e episódios de séries,
avaliar (nota de 0 a 10), ver histórico de visualização, criar listas
tipo "favoritos" ou "pra assistir", e tirar alguns relatórios (nota média
por gênero, tempo total assistido, top 10, etc).

O foco do trabalho é aplicar POO de verdade: herança (Midia -> Filme/Serie),
composição (Serie tem Temporadas, Temporada tem Episodios), encapsulamento
com @property pras validações, e os métodos especiais pedidos (__str__,
__eq__, __len__, __lt__).

Persistência vai ser em JSON (ou SQLite, ainda não decidi) via `dados.py`.

## Estrutura de classes (rascunho)

**Midia** (base)
- titulo, tipo (FILME/SERIE), genero, ano, duracao_minutos,
  classificacao_indicativa, elenco, status, nota, data_conclusao
- __str__/__repr__, __eq__ (compara por titulo+tipo), __lt__ (por nota)

**Filme(Midia)** - não tem muita coisa a mais, usa a duração/nota direto

**Serie(Midia)**
- lista de Temporadas
- calcula nota média a partir dos episódios
- atualiza status pra ASSISTIDA quando todo mundo assistiu
- __len__ retorna total de episódios

**Temporada**
- numero, lista de Episodios

**Episodio**
- numero_temporada, numero_episodio, titulo, duracao, data_lancamento,
  status, nota (opcional)

**Usuario**
- listas personalizadas + histórico

**ListaPersonalizada**
- nome + lista de mídias, adicionar/remover

Relação geral: Filme e Serie herdam de Midia. Serie agrega Temporada, que
agrega Episodio. Usuario agrega ListaPersonalizada e o histórico.

## UML textual

```
CLASSES

Midia
  atributos:
    - titulo: str
    - tipo: str            (FILME ou SERIE)
    - genero: str
    - ano: int
    - duracao_minutos: int
    - classificacao_indicativa: str
    - elenco: list[str]
    - status: str          (NAO ASSISTIDO, ASSISTINDO, ASSISTIDO)
    - nota: float          (0 a 10)
    - data_conclusao: datetime
  métodos:
    + marcar_concluida()
    + __str__() / __repr__()
    + __eq__(other)        compara por titulo + tipo
    + __lt__(other)        compara por nota

Filme (herda de Midia)
  atributos: nenhum extra
  métodos: nenhum extra

Serie (herda de Midia)
  atributos:
    - temporadas: list[Temporada]
  métodos:
    + adicionar_temporada(temporada)
    + nota_media()
    + atualizar_status()   vira ASSISTIDA quando todos os episódios forem assistidos
    + __len__()            total de episódios

Temporada
  atributos:
    - numero: int
    - episodios: list[Episodio]
  métodos:
    + adicionar_episodio(episodio)
    + __len__()            número de episódios da temporada

Episodio
  atributos:
    - numero_temporada: int
    - numero_episodio: int
    - titulo: str
    - duracao_minutos: int
    - data_lancamento: date
    - status: str
    - nota: float          (opcional, 0 a 10)
  métodos:
    + __str__() / __repr__()

Usuario
  atributos:
    - nome: str
    - listas: list[ListaPersonalizada]
    - historico: list[RegistroHistorico]
  métodos:
    + criar_lista(nome)
    + adicionar_favorito(midia, nome_lista)
    + registrar_conclusao(midia)

ListaPersonalizada
  atributos:
    - nome: str
    - midias: list[Midia]
  métodos:
    + adicionar(midia)
    + remover(midia)
    + __len__()

RegistroHistorico
  atributos:
    - midia: Midia
    - data_conclusao: datetime
  métodos:
    + __str__()


RELACIONAMENTOS

Filme  --herda--> Midia
Serie  --herda--> Midia

Serie     <>-- Temporada           composição (1 série tem 0..* temporadas)
Temporada <>-- Episodio            composição (1 temporada tem 0..* episódios)
Usuario   <>-- ListaPersonalizada  composição (1 usuário tem 0..* listas)
Usuario   <>-- RegistroHistorico   composição (1 usuário tem 0..* registros)

ListaPersonalizada  --> Midia      associação (uma lista referencia 0..* mídias)
RegistroHistorico   --> Midia      associação (um registro referencia 1 mídia)
```

`<>--` é o losango da composição (o "todo" fica do lado do losango) e
`-->` é associação simples.

## CLI (planejado)

```
midia adicionar
midia avaliar
midia listar
midia relatorio top
serie adicionar-episodio
serie atualizar-status
usuario criar-lista
usuario adicionar-favorito
```

## Rodando (ainda não funciona, só estrutura por enquanto)

```bash
python -m src.cli --help
```

## Testes

pytest, cobrindo criação/validação de mídias, cálculo de notas, tempo
assistido, duplicidade de título+tipo+ano, e os relatórios. Meta é pelo
menos 15 testes no final.

## Onde estou (semana 1)

- [x] estrutura de classes definida (esse README)
- [x] UML textual
- [x] classes vazias criadas, só com docstring dizendo o que cada uma faz
- [ ] implementação de verdade entra semana que vem