from dataclasses import dataclass

@dataclass
class Config:
    taxa_emissao_fonte: float = 1500.0  # [Ci/segundo]
    converter_ci_bq: bool = True

    altura_chamine: int = 100  # [m]
    velocidade_vento: float = 5.0  # [m/segundo]
    classe_estabilidade: str = "D"  # classe estabilidade atmosférica
    terreno: str = "R"  # R para rural, U para urbano

    gerar_meshgrid_xyz: bool = True
    dimensao_eixo_x: int = 20000  # [m] inteiro >= 1 e multiplo de passo_x
    dimensao_eixo_y: int = 2500  # [m] inteiro >= 0 e multiplo de passo_y
    dimensao_eixo_z: int = 1000  # [m] inteiro >= 0 e multiplo de passo_z
    passo_x: int = 50  # [m] inteiro >= 1
    passo_y: int = 25  # [m] inteiro >= 1
    passo_z: int = 10  # [m] inteiro >= 1
    limite_pontos: int = 12_500_000  # limite de pontos simulados (sugestão: 10^6 a 10^8)

    calcular_ponto_especifico: bool = True
    x_calculo: int = 2000
    y_calculo: int = 0
    z_calculo: int = 100

    plotar_heatmap_xy: bool = True
    z_corte: int = 0  # altura z do corte no plano xy
                                # multiplos de passo_z (ou zero)
                                # Obs.: zero para nivel do solo

    plotar_heatmap_yz: bool = True
    x_corte: int = 10000  # distancia x do corte no plano yz
                                  # multiplos de passo_x

    plotar_heatmap_xz: bool = True
    y_corte: int = 250  # lateralidade y do corte no plano xz
                                 # multiplos de passo_y

    gamma: float = 0.4  # 0.3 a 0.9
                           # proximo a 0.3 -> realça frios (baixas concentrações)
                           # proximo a 0.9 -> realça quentes (altas concentrações)

    unidade: str = "Ci"

    def __post_init__(self):
        if self.converter_ci_bq:
            self.taxa_emissao_fonte *= 3.7e10
            self.unidade = "Bq"
        else:
            self.unidade = "Ci"
