from dataclasses import dataclass

@dataclass
class Config:

    converter_ci_bq: bool = False
    unidade: str = "Ci"

    altura_chamine: int = 1         # [m]
    terreno: str = "R"              # R para rural, U para urbano

    vento_min: int = 4 	            #[m/s]
    vento_max: int = 6	            #[m/s]

    emissao_min: int = 8	        #[Ci minimo para um evento discreto]
    emissao_max: int = 12	        #[Ci máximo para um evento discreto]

    seed: int = 42
    total_eventos: int = 30	        #[eventos]

    vento_teste_fixo: int = 1
    emissao_teste_fixo: int = 1 
    classe_teste_fixo: str = "C"

    dimensao_eixo_x: int = 100       # [m] inteiro >= 1 e multiplo de passo_x
    dimensao_eixo_y: int = 25        # [m] inteiro >= 0 e multiplo de passo_y
    dimensao_eixo_z: int = 50        # [m] inteiro >= 0 e multiplo de passo_z
    passo_x: int = 1                 # [m] inteiro >= 1
    passo_y: int = 1                 # [m] inteiro >= 1
    passo_z: int = 1                 # [m] inteiro >= 1
    limite_pontos: int = 500_000     # limite de pontos por evento discreto (sugestão: 10^6)

    plotar_heatmap_xy: bool = True
    z_corte: int = 0                # altura z do corte no plano xy
                                    # multiplos de passo_z (ou zero)
                                    # Obs.: zero para nivel do solo

    plotar_heatmap_yz: bool = False
    x_corte: int = 50               # distancia x do corte no plano yz
                                    # multiplos de passo_x

    plotar_heatmap_xz: bool = False
    y_corte: int = 5                # lateralidade y do corte no plano xz
                                    # multiplos de passo_y

    gamma: float = 0.4              # 0.3 a 0.9
                                    # proximo a 0.3 -> realça frios (baixas concentrações)
                                    # proximo a 0.9 -> realça quentes (altas concentrações)

    diretorio_dados_parciais: str = "dados_parciais"
    diretorio_campos_parciais: str = "campos_parciais"
    diretorio_plotagens_parciais: str = "plotagens_parciais"
    diretorio_dados_acumulados: str = "dados_acumulados"
    diretorio_plotagens_acumuladas: str = "plotagens_acumuladas"