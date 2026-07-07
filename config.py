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

    seed: int = 42

    total_eventos: int = 48         #[eventos]
    intervalo_t_eventos: int = 900  #[segundos, para cada evento]

    vento_teste_fixo: int = 1       #modulo da velocidade do vento, em m/min
    angulo_teste_fixo: int = 0      #angulo do vento em graus (-360 a 360)
    emissao_teste_fixo: int = 1         
    classe_teste_fixo: str = "C"

    dimensao_eixo_x: int = 10000    # [m] inteiro >= 1 e multiplo de passo_x
    dimensao_eixo_y: int = 10000    # [m] inteiro >= 0 e multiplo de passo_y
    dimensao_eixo_z: int = 1        # [m] inteiro >= 0 e multiplo de passo_z
    passo_x: int = 20               # [m] inteiro >= 1
    passo_y: int = 20               # [m] inteiro >= 1
    passo_z: int = 1                # [m] inteiro >= 1
    limite_pontos: int = 1000000    # limite de pontos por evento discreto (sugestão: 10^6)

    simular_momento_a_momento: bool = True

    plotar_heatmap_xy: bool = True
    z_corte: int = 1                # altura z do corte no plano xy

    plotar_heatmap_yz: bool = False
    x_corte: int = 1000             # distancia x do corte no plano yz

    plotar_heatmap_xz: bool = False
    y_corte: int = 1000             # lateralidade y do corte no plano xz

    gamma: float = 0.4              # 0.3 a 0.9

    diretorio_dados_parciais: str = "dados_parciais"
    diretorio_campos_parciais: str = "campos_parciais"
    diretorio_plotagens_parciais: str = "plotagens_parciais"
    diretorio_dados_acumulados: str = "dados_acumulados"
    diretorio_plotagens_acumuladas: str = "plotagens_acumuladas"