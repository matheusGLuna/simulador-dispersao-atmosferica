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

    concentracoes_xy = None

    lista_puffs: List[Puff] = []

    for evento in range(config.total_eventos):

        idade = (config.total_eventos - evento) * config.intervalo_tempo_evento

    #    atividade_emitida = scenario.obter_taxa_emissao(evento)
    #    velocidade_vento = scenario.obter_velocidade_vento(evento)
    #    angulo_vento = scenario.obter_angulo_vento(evento)
    #    classe_estabilidade = scenario.obter_classe_estabilidade(evento)

        atividade_emitida = config.emissao_teste_fixo
        velocidade_vento = config.vento_teste_fixo
        angulo_vento_variante_teste = config.angulo_teste_fixo + evento*0
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

    if config.simular_acumulacao_resultante:
        
        for puff in lista_puffs:

            id_puff = puff.evento + 1
            
            (
                concentracoes_puff_xy,
                eixo_x,
                eixo_y
            ) = model.gerar_meshgrid_xy(
                puff
            )

            if concentracoes_xy is None:
                concentracoes_xy = np.zeros_like(concentracoes_puff_xy)

            np.add(
                concentracoes_xy,
                concentracoes_puff_xy,
                out=concentracoes_xy
            )

        if concentracoes_xy is not None:
            print("Campo resultante acumulado com sucesso\n")
            plotting.apresentar_maximo_campo(
                concentracoes_xy,
                eixo_x,
                eixo_y
            )
            plotting.plotar_campo_acumulado(
                concentracoes_xy,
                eixo_x,
                eixo_y
            )

        fim_clock_1 = datetime.now()
        fim_1 = time.perf_counter()
        print(f"Fim 1 : {fim_clock_1.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 1 : {fim_1 - inicio:.2f} segundos")   

    if config.simular_evolucao_temporal:

        for evento in range(config.total_eventos):

            print (f"evento {evento} sendo processado... ")
            concentracoes_xy = None

            for puff in lista_puffs:
                
                if puff.evento > evento:
                    continue
                
                idade_instantanea =  (evento - puff.evento + 1) * config.intervalo_tempo_evento
                puff.idade = idade_instantanea
                sigma_y = model.calcular_sigma_y(puff)

                distancias_cantos_malha = [
                    np.hypot(x, y)
                    for x in (-config.dim_eixo_x_neg, config.dim_eixo_x_pos)
                    for y in (-config.dim_eixo_y_neg, config.dim_eixo_y_pos)
                ]
                maxima_distancia_interesse = max(distancias_cantos_malha) + 5*sigma_y
                distancia_centro_instantanea = puff.idade*puff.velocidade_vento

                if maxima_distancia_interesse < distancia_centro_instantanea:
                    continue

                (
                    concentracoes_puff_xy,
                    eixo_x,
                    eixo_y
                ) = model.gerar_meshgrid_xy(
                    puff
                )

                if concentracoes_xy is None:
                    concentracoes_xy = np.zeros_like(concentracoes_puff_xy)

                np.add(
                    concentracoes_xy,
                    concentracoes_puff_xy,
                    out=concentracoes_xy
                )

            plotting.plotar_heatmap_xy(
                concentracoes_xy,
                eixo_x,
                eixo_y,
                evento + 1,
                exibir_maximo=False,
                campo_acumulado=False
            )

        fim_clock_2 = datetime.now()
        fim_2 = time.perf_counter()
        print(f"Fim 2 : {fim_clock_2.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 2 : {fim_2 - inicio:.2f} segundos")
