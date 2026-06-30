from dataclasses import dataclass

@dataclass
class Puff:

    evento: int                 # evento discreto da simulação associado a este puff (adimensional)

    idade: int                  # tempo decorrido desde a emissao deste puff [segundos]

    atividade_emitida: float    # atividade emitida por este puff [Ci ou Bq]

    velocidade_vento: float     # velocidade do vento no instante de emissao deste puff, na direção x [m/s]

    angulo_vento: float         #

    classe_estabilidade: str    # classe de estabilidade atmosférica associada ao instante da liberação deste puff
