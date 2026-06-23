from pathlib import Path

import numpy as np

from config import Config
from model import GaussianPlumeModel
from temporal_model import TemporalScenario
import plotting

if __name__ == "__main__":
    
    config = Config()
    model = GaussianPlumeModel(config)
    scenario = TemporalScenario(config)

    concentracoes_xyz = None
    diretorio_dados = (
        Path(config.diretorio_dados_parciais)
        / f"s{config.seed}"
        / config.diretorio_campos_parciais
    )
    diretorio_dados.mkdir(parents=True, exist_ok=True)

    for evento in range(config.total_eventos):

        velocidade_vento = (    
            scenario.obter_velocidade_vento(evento)
        )

        taxa_emissao = (
            scenario.obter_taxa_emissao(evento)
        )

        classe_estabilidade = (
            scenario.obter_classe_estabilidade(
                evento,
                config.total_eventos
            )
        )

        (
            concentracoes_evento_xyz,
            eixo_x,
            eixo_y,
            eixo_z
        ) = model.gerar_meshgrid_xyz(
            velocidade_vento,
            taxa_emissao,
            classe_estabilidade
        )

        if concentracoes_xyz is None:
            concentracoes_xyz = np.zeros_like(concentracoes_evento_xyz)

        np.add(
            concentracoes_xyz,
            concentracoes_evento_xyz,
            out=concentracoes_xyz
        )

        arquivo_evento = diretorio_dados / f"evento_{evento:02d}.npz"
        np.savez_compressed(
            arquivo_evento,
            concentracoes_xyz=concentracoes_evento_xyz,
            eixo_x=eixo_x,
            eixo_y=eixo_y,
            eixo_z=eixo_z,
            evento=evento,
            velocidade_vento=velocidade_vento,
            taxa_emissao=taxa_emissao,
            classe_estabilidade=classe_estabilidade
        )

        print(f"meshgrid de concentrações C(x,y,z) modelado com sucesso para o evento {evento}\n")

        if config.plotar_heatmap_xy:
            plotting.plotar_heatmap_xy(
                concentracoes_evento_xyz,
                eixo_x,
                eixo_y,
                evento,
                exibir_maximo=False,
                campo_acumulado=False
            )

        if config.plotar_heatmap_yz:
            plotting.plotar_heatmap_yz(
                concentracoes_evento_xyz,
                eixo_y,
                eixo_z,
                evento,
                exibir_maximo=False,
                campo_acumulado=False
            )

        if config.plotar_heatmap_xz:
            plotting.plotar_heatmap_xz(
                concentracoes_evento_xyz,
                eixo_x,
                eixo_z,
                evento,
                exibir_maximo=False,
                campo_acumulado=False
            )

    if concentracoes_xyz is not None:
        print("Campo resultante acumulado com sucesso\n")
        plotting.apresentar_maximos_cortes(
            concentracoes_xyz,
            eixo_x,
            eixo_y,
            eixo_z
        )
        plotting.plotar_cortes_acumulados(
            concentracoes_xyz,
            eixo_x,
            eixo_y,
            eixo_z
        )
