from pathlib import Path
from datetime import datetime
from typing import List
import shutil
import subprocess
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
    vmax_referencia = None

    lista_puffs: List[Puff] = []

    amplitude_variacao_angular = 10.0

    for evento in range(config.total_eventos):

        idade = (config.total_eventos - evento) * config.intervalo_tempo_evento

    #    atividade_emitida = scenario.obter_taxa_emissao(evento)
    #    velocidade_vento = scenario.obter_velocidade_vento(evento)
    #    angulo_vento = scenario.obter_angulo_vento(evento)
    #    classe_estabilidade = scenario.obter_classe_estabilidade(evento)

        atividade_emitida = config.emissao_teste_fixo
        velocidade_vento = config.vento_teste_fixo
        
        progresso = (
            evento / (config.total_eventos - 1)
            if config.total_eventos > 1
            else 0.0
        )
        angulo_vento_evento = np.interp(
            progresso,
            [0.0, 0.25, 0.50, 0.75, 1.0],
            [
                0.0,
                amplitude_variacao_angular,
                -amplitude_variacao_angular,
                amplitude_variacao_angular,
                0.0,
            ],
        )

        classe_estabilidade = config.classe_teste_fixo

        puff = Puff(
            evento = evento,
            idade = idade,
            atividade_emitida = atividade_emitida,
            velocidade_vento = velocidade_vento,
            angulo_vento=angulo_vento_evento,
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
            vmax_referencia = float(np.max(concentracoes_xy))
            print("Campo resultante acumulado com sucesso")
            print(f"Vmax de referência para os heatmaps: {vmax_referencia:.3e} {config.unidade}/m³")
            plotting.plotar_heatmap_xy(
                concentracoes_xy,
                eixo_x,
                eixo_y,
                campo_acumulado=True,
                vmax_referencia=vmax_referencia,
            )

        fim_clock_1 = datetime.now()
        fim_1 = time.perf_counter()
        print(f"Fim 1 : {fim_clock_1.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 1 : {fim_1 - inicio:.2f} segundos")   

    if config.simular_evolucao_temporal and vmax_referencia is None:
        print(
            "A evolução temporal requer a simulação acumulada para definir "
            "o vmax de referência. Habilite simular_acumulacao_resultante."
        )

    if config.simular_evolucao_temporal and vmax_referencia is not None:

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
                campo_acumulado=False,
                vmax_referencia=vmax_referencia,
            )

        fim_clock_2 = datetime.now()
        fim_2 = time.perf_counter()
        print(f"Fim 2 : {fim_clock_2.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 2 : {fim_2 - inicio:.2f} segundos")

        diretorio_plotagens = (
            Path(config.diretorio_dados_parciais)
            / f"cenario{config.seed}"
            / config.diretorio_plotagens_parciais
        )
        arquivo_video = diretorio_plotagens / "evolucao_temporal.mp4"
        ffmpeg = shutil.which("ffmpeg")

        if ffmpeg is None:
            print("FFmpeg não encontrado; o vídeo temporal não foi gerado.")
        else:
            comando_ffmpeg = [
                ffmpeg,
                "-y",
                "-framerate",
                "10",
                "-start_number",
                "1",
                "-i",
                str(diretorio_plotagens / "evento_%02d_heatmap_xy.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(arquivo_video),
            ]

            try:
                subprocess.run(comando_ffmpeg, check=True)
                print(f"Vídeo temporal salvo em: {arquivo_video}")
            except subprocess.CalledProcessError as error:
                print(f"Falha ao gerar o vídeo temporal: {error}")
