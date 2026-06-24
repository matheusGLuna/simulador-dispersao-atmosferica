from dataclasses import dataclass

@dataclass
class Puff:

    instante_emissao: float       # momento da simulacao da liberacao do jato, em segundos

    atividade_emitida: float      # atividade emitida pelo jato, em Ci

    velocidade_vento: float       # velocidade média do vento no instante de emissao, em m/s

    classe_estabilidade: str

