from config import Config
from model import GaussianPlumeModel
from temporal_model import TemporalScenario
import plotting

if __name__ == "__main__":
    
    config = Config()
    model = GaussianPlumeModel(config)
    scenario = TemporalScenario(config)

    if config.calcular_ponto_especifico:
            
        x_particular = abs(config.x_calculo)
        y_particular = abs(config.y_calculo)
        z_particular = abs(config.z_calculo)

        concentracao = model.calcular_concentracao(
            x_particular,
            y_particular,
            z_particular,
            velocidade_vento=config.vento_calculo_fixo,
            taxa_emissao=config.emissao_calculo_fixa,
            classe_estabilidade=config.classe_estabilidade_calculo_fixa
        )

        print(
            f"No ponto solicitado: C({x_particular},{y_particular},{z_particular}) = "
            f"{concentracao:.3e} {config.unidade}/m³\n"
        )

    plotagem_realizada = False

    for evento in range(config.total_eventos):

        velocidade_vento = (    
            scenario.obter_velocidade_vento(evento)
        )

        taxa_emissao = (
            scenario.obter_taxa_emissao(evento)
        )

        taxa_emissao = 100 # Temporario para teste - sobrepondo com taxa fixa

        classe_estabilidade = (
            scenario.obter_classe_estabilidade(
                evento,
                config.total_eventos
            )
        )

        classe_estabilidade = 'C'  # Temporario para teste - sobrepondo com classe fixa

        (
            concentracoes_xyz,
            eixo_x,
            eixo_y,
            eixo_z
        ) = model.gerar_meshgrid_xyz(
            velocidade_vento,
            taxa_emissao,
            classe_estabilidade
        )
        
        if config.plotar_heatmap_xy:
            plotting.plotar_heatmap_xy(concentracoes_xyz, eixo_x, eixo_y, evento)
            plotagem_realizada = True

        if config.plotar_heatmap_yz:
            plotting.plotar_heatmap_yz(concentracoes_xyz, eixo_y, eixo_z, evento)
            plotagem_realizada = True

        if config.plotar_heatmap_xz:
            plotting.plotar_heatmap_xz(concentracoes_xyz, eixo_x, eixo_z, evento)
            plotagem_realizada = True

        print(f"meshgrid de concentrações C(x,y,z) modelado com sucesso para o evento {evento}\n")

    if plotagem_realizada:
        plotting.show_heatmap()
        print("Heatmaps 2D gerados com sucesso\n")