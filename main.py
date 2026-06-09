from config import Config
from model import GaussianPlumeModel
import plotting

if __name__ == "__main__":
    
    config = Config()
    model = GaussianPlumeModel(config)
    
    # ============================================================================
    # Gera meshgrid 3d de concentrações C(x,y,z) para todos os pontos no espaço
    # ============================================================================
    concentracoes_xyz, eixo_x, eixo_y, eixo_z = (model.gerar_meshgrid_xyz())
    print("meshgrid de concentrações C(x,y,z) modelado com sucesso\n")

    if config.calcular_ponto_especifico:    
        x_particular = abs(config.x_calculo)
        y_particular = abs(config.y_calculo)
        z_particular = abs(config.z_calculo)

        concentracao = model.calcular_concentracao(
            x_particular,
            y_particular,
            z_particular,
        )

        print(
            f"No ponto solicitado: C({x_particular},{y_particular},{z_particular}) = "
            f"{concentracao:.3e} {config.unidade}/m³\n"
        )

    if config.plotar_heatmap_xy:
        plotting.plotar_heatmap_xy(concentracoes_xyz, eixo_x, eixo_y)

    if config.plotar_heatmap_yz:
        plotting.plotar_heatmap_yz(concentracoes_xyz, eixo_y, eixo_z)

    if config.plotar_heatmap_xz:
        plotting.plotar_heatmap_xz(concentracoes_xyz, eixo_x, eixo_z)

    if any([config.plotar_heatmap_xy, config.plotar_heatmap_yz, config.plotar_heatmap_xz]):
        plotting.show_heatmap()
        print("Heatmaps 2D gerados com sucesso\n")
