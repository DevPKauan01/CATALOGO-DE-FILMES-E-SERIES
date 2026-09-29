"""Configuracoes do sistema, lidas do settings.json."""

from __future__ import annotations


class Configuracoes:
    """Parametros configuraveis do catalogo.

    Atributos:
        nota_minima_recomendado: nota minima pra uma midia ser "recomendada".
        limite_listas_por_usuario: maximo de listas personalizadas por usuario.
        multiplicador_duracao: fator pra converter minutos em horas.
        casas_decimais_horas: casas decimais no arredondamento das horas.
    """

    def __init__(
        self,
        nota_minima_recomendado: float = 7.5,
        limite_listas_por_usuario: int = 10,
        multiplicador_duracao: float = 1 / 60,
        casas_decimais_horas: int = 1,
    ) -> None:
        self.nota_minima_recomendado = nota_minima_recomendado
        self.limite_listas_por_usuario = limite_listas_por_usuario
        self.multiplicador_duracao = multiplicador_duracao
        self.casas_decimais_horas = casas_decimais_horas

    @classmethod
    def carregar(cls, caminho: str = "settings.json") -> Configuracoes:
        """Le o settings.json e devolve as configuracoes."""
        raise NotImplementedError

    def minutos_para_horas(self, minutos: int) -> float:
        """Converte minutos em horas usando multiplicador e arredondamento."""
        raise NotImplementedError
