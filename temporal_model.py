import random

from config import Config

class TemporalScenario:

    def __init__(self, config: Config):
        self.config = config
        self.rng = random.Random(config.seed)

    def obter_velocidade_vento(self, evento):
        """
        Retorna a velocidade do vento [m/s]
        para um determinado evento temporal.
        """

        return self.rng.randint(
            self.config.vento_min,
            self.config.vento_max
        )

    def obter_taxa_emissao(self, evento):
        """
        Retorna a emissão total do evento [Ci].
        """
        taxa = self.rng.randint(
            self.config.emissao_min,
            self.config.emissao_max
        )

        if self.config.converter_ci_bq:
            taxa *= 3.7e10
            
        return taxa

    def obter_classe_estabilidade(
        self,
        evento
    ):
        """
        Distribuição simplificada baseada
        na hora do dia.
        """

        fracao = evento / self.config.total_eventos

        # madrugada
        if fracao < 0.25:
            return self.rng.choice(["E", "F"])

        # manhã
        elif fracao < 0.42:
            return "D"

        # período mais instável
        elif fracao < 0.67:
            return self.rng.choice(["A", "B"])

        # tarde
        elif fracao < 0.84:
            return self.rng.choice(["C", "D"])

        # noite
        else:
            return self.rng.choice(["E", "F"])