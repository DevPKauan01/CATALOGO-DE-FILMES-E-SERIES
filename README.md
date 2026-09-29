# Catálogo de Filmes e Séries

Projeto 1 de POO (UFCA - Eng. de Software) - Tema 10.

## Sobre o projeto

A ideia é um CLI pra gerenciar um catálogo pessoal de filmes e séries.
Dá pra cadastrar mídias, acompanhar temporadas e episódios de séries,
avaliar (nota de 0 a 10), ver histórico de visualização, criar listas
tipo "favoritos" ou "pra assistir", e tirar relatórios (nota média por
gênero, tempo total assistido, top 10, etc).

O foco do trabalho é aplicar POO de verdade: herança (Midia -> Filme/Serie),
composição (Serie tem Temporadas, Temporada tem Episodios), encapsulamento
com `@property` pras validações, e os métodos especiais pedidos (`__str__`,
`__repr__`, `__eq__`, `__len__`, `__lt__`).

Persistência vai ser em JSON via `dados.py`, e as configurações ficam no
`settings.json`.

## Estrutura do projeto

```
.
├── README.md
├── settings.json
└── src
    ├── cli.py                  # interface de linha de comando
    ├── catalogo.py             # Catalogo: guarda mídias, impede duplicidade
    ├── configuracoes.py        # Configuracoes: lê o settings.json
    ├── dados.py                # salvar/carregar (JSON) e seed
    ├── relatorios.py           # relatórios do catálogo
    └── models
        ├── enums.py            # TipoMidia, StatusVisualizacao
        ├── midia.py            # Midia (base)
        ├── filme.py            # Filme
        ├── serie.py            # Serie
        ├── temporada.py        # Temporada
        ├── episodio.py         # Episodio
        ├── usuario.py          # Usuario
        ├── lista_personalizada.py
        └── registro_historico.py
```

## Estrutura de classes

| Classe | Papel |
|---|---|
| `Midia` | classe base de filmes e séries |
| `Filme` | herda de Midia, fixa tipo FILME |
| `Serie` | herda de Midia, agrega Temporadas, nota e duração calculadas |
| `Temporada` | agrupa Episodios de uma Serie |
| `Episodio` | unidade assistível de uma Serie, com nota opcional |
| `Usuario` | dono das listas personalizadas e do histórico |
| `ListaPersonalizada` | lista nomeada de mídias ("Favoritos", "Pra assistir") |
| `RegistroHistorico` | data/hora de conclusão de uma mídia |
| `Catalogo` | coleção de mídias; garante que não haja duplicidade |
| `Configuracoes` | parâmetros do `settings.json` |
| `TipoMidia`, `StatusVisualizacao` | enums do domínio |

## UML textual

```
ENUMS

TipoMidia:            FILME | SERIE
StatusVisualizacao:   NÃO ASSISTIDO | ASSISTINDO | ASSISTIDO


CLASSES

Midia
  atributos:
    - titulo: str                       (não vazio)
    - tipo: TipoMidia
    - genero: str
    - ano: int
    - duracao_minutos: int | None       (> 0; None em Serie)
    - classificacao_indicativa: str
    - elenco: list[str]
    - status: StatusVisualizacao
    - nota: float | None                (0 a 10)
    - data_conclusao: datetime | None
  métodos:
    + duracao_total() -> int            Filme: a própria; Serie: soma dos episódios
    + nota_media() -> float | None      Serie sobrescreve
    + marcar_concluida(quando)
    + __str__() / __repr__()
    + __eq__(other)                     compara por titulo + tipo
    + __lt__(other)                     compara por nota média

Filme (herda de Midia)
  atributos: nenhum extra (tipo fixo em FILME)
  métodos: nenhum extra

Serie (herda de Midia)
  atributos:
    - temporadas: list[Temporada]       (tipo fixo em SERIE)
  métodos:
    + adicionar_temporada(temporada)
    + episodios_assistidos() -> int
    + nota_media() -> float | None      média das notas dos episódios
    + atualizar_status()                vira ASSISTIDO quando todos os episódios forem
    + __len__()                         total de episódios

Temporada
  atributos:
    - numero: int                       (> 0)
    - episodios: list[Episodio]
  métodos:
    + adicionar_episodio(episodio)
    + todos_assistidos() -> bool
    + __len__()                         número de episódios da temporada

Episodio
  atributos:
    - numero_temporada: int             (> 0)
    - numero_episodio: int              (> 0)
    - titulo: str                       (não vazio)
    - duracao_minutos: int              (> 0)
    - data_lancamento: date
    - status: StatusVisualizacao
    - nota: float | None                (0 a 10, opcional)
    - data_conclusao: datetime | None
  métodos:
    + marcar_assistido(quando)
    + __str__() / __repr__()

Usuario
  atributos:
    - nome: str
    - configuracoes: Configuracoes
    - listas: list[ListaPersonalizada]
    - historico: list[RegistroHistorico]
  métodos:
    + criar_lista(nome)                 respeita o limite do settings.json
    + obter_lista(nome)
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

Catalogo
  atributos:
    - midias: list[Midia]
  métodos:
    + adicionar(midia)                  recusa duplicidade (titulo + tipo + ano)
    + existe(titulo, tipo, ano) -> bool
    + buscar(titulo, tipo) -> list[Midia]
    + concluidas() -> list[Midia]       só status ASSISTIDO
    + nota_geral() -> float | None
    + __len__()

Configuracoes
  atributos:
    - nota_minima_recomendado: float
    - limite_listas_por_usuario: int
    - multiplicador_duracao: float      minutos -> horas
    - casas_decimais_horas: int         arredondamento
  métodos:
    + carregar(caminho)                 (classmethod, lê o settings.json)
    + minutos_para_horas(minutos) -> float


RELACIONAMENTOS

Filme  --herda--> Midia
Serie  --herda--> Midia

Serie     <>-- Temporada           composição (1 série tem 0..* temporadas)
Temporada <>-- Episodio            composição (1 temporada tem 0..* episódios)
Usuario   <>-- ListaPersonalizada  composição (1 usuário tem 0..* listas)
Usuario   <>-- RegistroHistorico   composição (1 usuário tem 0..* registros)
Catalogo  <>-- Midia               agregação  (1 catálogo tem 0..* mídias)

ListaPersonalizada  --> Midia          associação (uma lista referencia 0..* mídias)
RegistroHistorico   --> Midia          associação (um registro referencia 1 mídia)
Usuario             --> Configuracoes  associação (usa o limite de listas)
```

`<>--` é o losango (o "todo" fica do lado do losango) e `-->` é associação
simples.

## Relatórios (funções em `relatorios.py`)

- `media_por_genero`: nota média por gênero
- `tempo_assistido_por_tipo`: horas assistidas de filme e de série
- `top_melhores`: top 10 filmes/séries mais bem avaliados
- `series_mais_assistidas`: séries com mais episódios assistidos
- `tempo_assistido_no_periodo`: tempo assistido por semana/mês

Todos consideram só mídias com status ASSISTIDO.

## Configurações (`settings.json`)

```json
{
  "nota_minima_recomendado": 7.5,
  "limite_listas_por_usuario": 10,
  "multiplicador_duracao": 0.0166667,
  "casas_decimais_horas": 1
}
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
- [x] classes criadas com atributos e docstrings, sem lógica ainda
