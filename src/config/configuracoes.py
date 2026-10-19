"""Configuracoes do sistema, lidas do settings.json."""

from __future__ import annotations

import json
import os


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
        """Le o settings.json e devolve as configuracoes.

        Se o arquivo nao existir, usa os valores padrao. Chaves que faltarem
        no arquivo tambem ficam com o valor padrao.
        """
        if not os.path.exists(caminho):
            return cls()
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return cls(
            nota_minima_recomendado=dados.get("nota_minima_recomendado", 7.5),
            limite_listas_por_usuario=dados.get("limite_listas_por_usuario", 10),
            multiplicador_duracao=dados.get("multiplicador_duracao", 1 / 60),
            casas_decimais_horas=dados.get("casas_decimais_horas", 1),
        )

    def minutos_para_horas(self, minutos: int) -> float:
        """Converte minutos em horas usando multiplicador e arredondamento."""
        return round(minutos * self.multiplicador_duracao, self.casas_decimais_horas)
