import json
import math
import re
from pathlib import Path

from config import Config
from puff import Puff


class LLMScenarioGenerator:
    """Carrega e valida cenários de puffs produzidos em formato JSON."""

    campos_puff = set(Puff.__dataclass_fields__)
    campos_puff_obrigatorios = campos_puff - {"idade"}
    classes_estabilidade_validas = {"A", "B", "C", "D", "E", "F"}

    def __init__(self, config: Config):
        self.config = config

    def gerar_lista_puffs(self, arquivo_cenario):
        """Lê um arquivo JSON e retorna a lista validada de objetos Puff."""
        caminho = Path(arquivo_cenario)

        try:
            dados_cenario = json.loads(caminho.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Arquivo de cenário não encontrado: {caminho}"
            ) from error
        except json.JSONDecodeError as error:
            raise ValueError(
                f"O arquivo de cenário contém JSON inválido: {caminho}"
            ) from error

        if not isinstance(dados_cenario, dict):
            raise ValueError(
                "O cenário deve ser um objeto JSON com metadados e eventos"
            )

        metadados = dados_cenario.get("metadados")
        eventos = dados_cenario.get("eventos")

        if not isinstance(metadados, dict):
            raise ValueError("O cenário deve conter metadados em JSON")

        cenario_id = metadados.get("cenario_id")
        if (
            not isinstance(cenario_id, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", cenario_id)
        ):
            raise ValueError(
                "metadados.cenario_id deve conter apenas letras, números, "
                "hífens e sublinhados"
            )

        delta_t_s = self.validar_inteiro_positivo(
            metadados.get("delta_t_s"),
            "metadados.delta_t_s",
        )

        if not isinstance(eventos, list) or not eventos:
            raise ValueError("eventos deve ser uma lista JSON não vazia de puffs")

        self.cenario_id = cenario_id
        self.delta_t_s = delta_t_s

        lista_puffs = [
            self.criar_puff(dados_puff, indice, delta_t_s)
            for indice, dados_puff in enumerate(eventos)
        ]
        self.validar_eventos(lista_puffs)

        return lista_puffs

    def criar_puff(self, dados_puff, indice, delta_t_s):
        """Valida um item do JSON e cria seu objeto Puff correspondente."""
        if not isinstance(dados_puff, dict):
            raise ValueError(f"Puff no índice {indice} deve ser um objeto JSON")

        campos_recebidos = set(dados_puff)
        campos_ausentes = self.campos_puff_obrigatorios - campos_recebidos
        campos_desconhecidos = campos_recebidos - self.campos_puff

        if campos_ausentes or campos_desconhecidos:
            detalhes = []
            if campos_ausentes:
                detalhes.append(f"campos ausentes: {sorted(campos_ausentes)}")
            if campos_desconhecidos:
                detalhes.append(f"campos desconhecidos: {sorted(campos_desconhecidos)}")
            raise ValueError(f"Puff no índice {indice} possui {', '.join(detalhes)}")

        evento = self.validar_inteiro_nao_negativo(
            dados_puff["evento"], "evento", indice
        )
        idade = delta_t_s
        atividade_emitida = self.validar_numero_nao_negativo(
            dados_puff["atividade_emitida"], "atividade_emitida", indice
        )
        atividade_emitida *= self.config.fator_conversao_atividade
        velocidade_vento = self.validar_numero_positivo(
            dados_puff["velocidade_vento"], "velocidade_vento", indice
        )
        angulo_vento = self.validar_numero_finito(
            dados_puff["angulo_vento"], "angulo_vento", indice
        )
        classe_estabilidade = dados_puff["classe_estabilidade"]

        if (
            not isinstance(classe_estabilidade, str)
            or classe_estabilidade not in self.classes_estabilidade_validas
        ):
            raise ValueError(
                f"classe_estabilidade do puff no índice {indice} deve ser uma "
                "letra maiúscula entre A e F"
            )

        return Puff(
            evento=evento,
            idade=idade,
            atividade_emitida=atividade_emitida,
            velocidade_vento=velocidade_vento,
            angulo_vento=angulo_vento,
            classe_estabilidade=classe_estabilidade,
        )

    @staticmethod
    def validar_inteiro_positivo(valor, campo):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise ValueError(f"{campo} deve ser um inteiro positivo")
        return valor

    @staticmethod
    def validar_inteiro_nao_negativo(valor, campo, indice):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError(
                f"{campo} do puff no índice {indice} deve ser um inteiro não negativo"
            )
        return valor

    @staticmethod
    def validar_numero_positivo(valor, campo, indice):
        valor_validado = LLMScenarioGenerator.validar_numero_finito(
            valor, campo, indice
        )
        if valor_validado <= 0:
            raise ValueError(
                f"{campo} do puff no índice {indice} deve ser maior que zero"
            )
        return valor_validado

    @staticmethod
    def validar_numero_nao_negativo(valor, campo, indice):
        valor_validado = LLMScenarioGenerator.validar_numero_finito(
            valor, campo, indice
        )
        if valor_validado < 0:
            raise ValueError(
                f"{campo} do puff no índice {indice} deve ser maior ou igual a zero"
            )
        return valor_validado

    @staticmethod
    def validar_numero_finito(valor, campo, indice):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{campo} do puff no índice {indice} deve ser numérico")

        valor_validado = float(valor)
        if not math.isfinite(valor_validado):
            raise ValueError(
                f"{campo} do puff no índice {indice} deve ser um número finito"
            )
        return valor_validado

    @staticmethod
    def validar_eventos(lista_puffs):
        eventos = sorted(puff.evento for puff in lista_puffs)
        eventos_esperados = list(range(len(lista_puffs)))

        if eventos != eventos_esperados:
            raise ValueError(
                "Os valores de evento devem ser únicos e sequenciais, de 0 até "
                f"{len(lista_puffs) - 1}"
            )
