from pathlib import Path

import numpy as np
import plotting

from config import Config
from model import GaussianPuffModel
from temporal_model import TemporalScenario
from puff import Puff

if __name__ == "__main__":
    
    config = Config()
    model = GaussianPuffModel(config)
    scenario = TemporalScenario(config)

    concentracoes_xyz = None
    # diretorio_dados = (
    #     Path(config.diretorio_dados_parciais)
    #     / f"s{config.seed}"
    #     / config.diretorio_campos_parciais
    # )
    # diretorio_dados.mkdir(parents=True, exist_ok=True)

    lista_puffs = []

    for evento in range(config.total_eventos):

    #    velocidade_vento = scenario.obter_velocidade_vento(evento)
    #    emissao = scenario.obter_taxa_emissao(evento)
    #    classe_estabilidade = scenario.obter_classe_estabilidade(evento)

        velocidade_vento = config.vento_teste_fixo
        emissao = config.emissao_teste_fixo
        classe_estabilidade = config.classe_teste_fixo

        puff = Puff(
            instante_emissao = evento,
            atividade_emitida = emissao,
            velocidade_vento = velocidade_vento,
            classe_estabilidade = classe_estabilidade
        )

        lista_puffs.append(puff)

    for puff in lista_puffs:

        (
            concentracoes_puff_xyz,
            eixo_x,
            eixo_y,
            eixo_z
        ) = model.gerar_meshgrid_xyz(
            puff
        )

        if concentracoes_xyz is None:
            concentracoes_xyz = np.zeros_like(concentracoes_puff_xyz)

        np.add(
            concentracoes_xyz,
            concentracoes_puff_xyz,
            out=concentracoes_xyz
        )

        # arquivo_evento = diretorio_dados / f"evento_{puff.instante_emissao:02d}.npz"
        # np.savez_compressed(
        #     arquivo_evento,
        #     concentracoes_xyz=concentracoes_puff_xyz,
        #     eixo_x=eixo_x,
        #     eixo_y=eixo_y,
        #     eixo_z=eixo_z,
        #     evento=puff.instante_emissao,
        #     velocidade_vento=velocidade_vento,
        #     emissao=emissao,
        #     classe_estabilidade=classe_estabilidade
        # )

        print(f"meshgrid de concentrações C(x,y,z) modelado com sucesso para o jato puff {puff.instante_emissao}\n")

        if config.plotar_heatmap_xy:
            plotting.plotar_heatmap_xy(
                concentracoes_puff_xyz,
                eixo_x,
                eixo_y,
                puff.instante_emissao,
                exibir_maximo=False,
                campo_acumulado=False
            )

        if config.plotar_heatmap_yz:
            plotting.plotar_heatmap_yz(
                concentracoes_puff_xyz,
                eixo_y,
                eixo_z,
                puff.instante_emissao,
                exibir_maximo=False,
                campo_acumulado=False
            )

        if config.plotar_heatmap_xz:
            plotting.plotar_heatmap_xz(
                concentracoes_puff_xyz,
                eixo_x,
                eixo_z,
                puff.instante_emissao,
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
