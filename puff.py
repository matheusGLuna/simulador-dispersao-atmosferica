from dataclasses import dataclass

@dataclass
class Puff:

    evento: int                 # numero inteiro identificador do evento discreto dentro do cenário simulado que representa este puff [adimensional]

    idade: int                  # numero inteiro que representa o tempo decorrido desde a emissao deste puff até o instante simulado [segundos]

    atividade_emitida: float    # numero real positivo que representa a atividade radioativa emitida por este puff [Ci ou Bq, conforme Config.converter_ci_bq]

    velocidade_vento: float     # numero real positivo que representa a velocidade do vento no instante de emissao deste puff, na direção x [m/s]

    angulo_vento: float         # numero real que representa o ângulo do vento no instante de emissao deste puff em relação ao eixo x [graus]

    classe_estabilidade: str    # Letra maiúscula, representando a classe de estabilidade atmosférica associada ao instante da liberação deste puff [A, B, C, D, E ou F]
