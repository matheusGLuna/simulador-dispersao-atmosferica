from dataclasses import dataclass

@dataclass
class Config:

    converter_ci_bq: bool = False
    unidade: str = "Ci"

    altura_chamine: int = 5         # [m]
    terreno: str = "R"              # R para rural, U para urbano

    vento_min: int = 1 	            #[m/s]
    vento_max: int = 3	            #[m/s]

    emissao_min: int = 8	        #[Ci minimo para um evento discreto]
    emissao_max: int = 12	        #[Ci máximo para um evento discreto]

    seed: int = 1

    total_eventos: int = 15             #[eventos]
    intervalo_tempo_evento: int = 30    #[segundos, para cada evento]

    vento_teste_fixo: int = 1       #modulo da velocidade do vento, em m/min
    angulo_teste_fixo: int = 0      #angulo do vento em graus (-360 a 360)
    emissao_teste_fixo: int = 1         
    classe_teste_fixo: str = "C"

    dim_eixo_x_pos: int = 500       # [m] inteiro >= 1 e multiplo de passo_x
    dim_eixo_x_neg: int = 0         # [m] inteiro >= 0 e multiplo de passo_x
    dim_eixo_y_pos: int = 250       # [m] inteiro >= 1 e multiplo de passo_y
    dim_eixo_y_neg: int = 250       # [m] inteiro >= 0 e multiplo de passo_y
    passo_x: int = 1                # [m] inteiro >= 1
    passo_y: int = 1                # [m] inteiro >= 1
    limite_pontos: int = 500000     # limite de pontos por malha calculada

    simular_acumulacao_resultante: bool = True
    simular_evolucao_temporal: bool = True

    gamma: float = 0.3              # 0.2 a 0.8

    diretorio_dados_parciais: str = "dados_parciais"
    diretorio_plotagens_parciais: str = "plotagens_parciais"
    diretorio_dados_acumulados: str = "dados_acumulados"
    diretorio_plotagens_acumuladas: str = "plotagens_acumuladas"
