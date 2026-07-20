from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import time

import numpy as np
import plotting

from config import Config
from model import GaussianPuffModel
from scenario_generator import LLMScenarioGenerator

if __name__ == "__main__":

    inicio_clock = datetime.now()
    inicio = time.perf_counter()
    print(f"Início: {inicio_clock.strftime('%Y-%m-%d %H:%M:%S')}")

    config = Config()
    model = GaussianPuffModel(config)
    scenario_generator = LLMScenarioGenerator(config)

    concentracoes_xy = None
    vmax_referencia = None

    lista_puffs = scenario_generator.gerar_lista_puffs(config.arquivo_cenario)
    cenario_id = scenario_generator.cenario_id
    total_eventos = len(lista_puffs)

    if config.simular_campo__acumulado:
        
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
                cenario_id=cenario_id,
            )

        fim_clock_1 = datetime.now()
        fim_1 = time.perf_counter()
        print(f"Fim 1 : {fim_clock_1.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 1 : {fim_1 - inicio:.2f} segundos")   

    if config.simular_animacao_temporal and vmax_referencia is None:
        print(
            "A animação temporal requer a execução da simulação do campo acumulado para definir "
            "o vmax de referência. Habilite simular_campo_acumulado."
        )

    if config.simular_animacao_temporal and vmax_referencia is not None:
        
        if len(lista_puffs) == 1:
            raise ValueError("A animação temporal requer um cenario com pelo menos dois eventos puff")
        else:
            intervalo_tempo_eventos = lista_puffs[0].idade - lista_puffs[1].idade

        for evento in range(total_eventos):

            concentracoes_xy = None

            for puff in lista_puffs:
                
                if puff.evento > evento:
                    continue
                
                idade_instantanea =  (evento - puff.evento + 1) * intervalo_tempo_eventos
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
                cenario_id=cenario_id,
            )

            print (f"evento {evento} processado")

        fim_clock_2 = datetime.now()
        fim_2 = time.perf_counter()
        print(f"Fim 2 : {fim_clock_2.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 2 : {fim_2 - inicio:.2f} segundos")

        diretorio_plotagens = (
            Path(config.diretorio_dados_parciais)
            / cenario_id
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
