from pathlib import Path
from datetime import datetime
from typing import List
import time

import numpy as np
import plotting

from config import Config
from model import GaussianPuffModel
from temporal_model import TemporalScenario
from puff import Puff

if __name__ == "__main__":

    inicio_clock = datetime.now()
    inicio = time.perf_counter()
    print(f"Início: {inicio_clock.strftime('%Y-%m-%d %H:%M:%S')}")

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

    lista_puffs: List[Puff] = []

    for evento in range(config.total_eventos):

        idade = (config.total_eventos - evento) * config.intervalo_t_eventos

    #    atividade_emitida = scenario.obter_taxa_emissao(evento)
    #    velocidade_vento = scenario.obter_velocidade_vento(evento)
    #    angulo_vento = scenario.obter_???(evento)
    #    classe_estabilidade = scenario.obter_classe_estabilidade(evento)

        atividade_emitida = config.emissao_teste_fixo
        velocidade_vento = config.vento_teste_fixo
        angulo_vento_variante_teste = config.angulo_teste_fixo + 0.1*evento
        classe_estabilidade = config.classe_teste_fixo

        puff = Puff(
            evento = evento,
            idade = idade,
            atividade_emitida = atividade_emitida,
            velocidade_vento = velocidade_vento,
            angulo_vento = angulo_vento_variante_teste,
            classe_estabilidade = classe_estabilidade
        )

        lista_puffs.append(puff)

    for puff in lista_puffs:

        id_puff = puff.evento + 1
        
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

        # print(f"meshgrid modelado com sucesso para o puff {id_puff}\n")

        # if config.plotar_heatmap_xy:
        #     plotting.plotar_heatmap_xy(
        #         concentracoes_puff_xyz,
        #         eixo_x,
        #         eixo_y,
        #         eixo_z,
        #         id_puff,
        #         exibir_maximo=False,
        #         campo_acumulado=False
        #     )

        # if config.plotar_heatmap_yz:
        #     plotting.plotar_heatmap_yz(
        #         concentracoes_puff_xyz,
        #         eixo_y,
        #         eixo_z,
        #         id_puff,
        #         exibir_maximo=False,
        #         campo_acumulado=False
        #     )

        # if config.plotar_heatmap_xz:
        #     plotting.plotar_heatmap_xz(
        #         concentracoes_puff_xyz,
        #         eixo_x,
        #         eixo_z,
        #         id_puff,
        #         exibir_maximo=False,
        #         campo_acumulado=False
        #     )

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

    fim_clock_1 = datetime.now()
    fim_1 = time.perf_counter()
    print(f"Fim 1 : {fim_clock_1.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tempo de processamento 1 : {fim_1 - inicio:.2f} segundos")   

    if config.simular_momento_a_momento:

        concentracoes_xyz = None

        for evento in range(config.total_eventos):

            print (f"evento {evento} de {config.total_eventos} sendo processado")

            for puff in lista_puffs:
                
                if puff.evento > evento:
                    continue
                
                idade_instantanea =  (evento - puff.evento + 1) * config.intervalo_t_eventos
                puff.idade = idade_instantanea
                sigma_y = model.calcular_sigma_y(puff)

                maxima_distancia_interesse = np.sqrt(config.dimensao_eixo_x**2 + config.dimensao_eixo_y**2) + 5*sigma_y
                distancia_centro_instantanea = puff.idade*puff.velocidade_vento

                if maxima_distancia_interesse < distancia_centro_instantanea:
                    continue

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

            if config.plotar_heatmap_xy:
                plotting.plotar_heatmap_xy(
                    concentracoes_xyz,
                    eixo_x,
                    eixo_y,
                    eixo_z,
                    evento + 1,
                    exibir_maximo=False,
                    campo_acumulado=False
                )

        fim_clock_2 = datetime.now()
        fim_2 = time.perf_counter()
        print(f"Fim 2 : {fim_clock_2.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 2 : {fim_2 - inicio:.2f} segundos")