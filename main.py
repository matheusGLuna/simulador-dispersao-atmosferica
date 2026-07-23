from datetime import datetime
from pathlib import Path
import time

import numpy as np
import plotting

from config import Config
from model import GaussianPuffModel
from scenario_generator import LLMScenarioGenerator


def main():

    inicio_clock = datetime.now()
    inicio = time.perf_counter()
    print(f"Início: {inicio_clock.strftime('%Y-%m-%d %H:%M:%S')}")

    config = Config()
    model = GaussianPuffModel(config)
    scenario_generator = LLMScenarioGenerator(config)

    lista_puffs = scenario_generator.gerar_lista_puffs(config.arquivo_cenario)
    cenario_id = scenario_generator.cenario_id
    total_eventos = len(lista_puffs)
    diretorio_plotagens = (
        Path(config.diretorio_dados_parciais)
        / cenario_id
        / config.diretorio_plotagens_parciais
    )

    if config.gerar_video_temporal and not config.gerar_plotagens_temporais:
        plotting.gerar_video_temporal(diretorio_plotagens)
        return

    if len(lista_puffs) == 1:
        raise ValueError(
            "A simulação temporal requer um cenário com pelo menos dois eventos"
        )

    intervalo_tempo_eventos = scenario_generator.delta_t_s
    distancias_cantos_malha = [
        np.hypot(x, y)
        for x in (-config.dim_eixo_x_neg, config.dim_eixo_x_pos)
        for y in (-config.dim_eixo_y_neg, config.dim_eixo_y_pos)
    ]
    distancia_maxima_malha = max(distancias_cantos_malha)
    X, Y, eixo_x, eixo_y = model.gerar_malha_xy()

    if config.gerar_plotagens_temporais:
        diretorio_campos = (
            Path(config.diretorio_dados_parciais)
            / cenario_id
            / "campos_temporais"
        )
        diretorio_campos.mkdir(parents=True, exist_ok=True)
        arquivo_campos = diretorio_campos / "concentracoes_temporais.npy"
        arquivo_eixo_x = diretorio_campos / "eixo_x.npy"
        arquivo_eixo_y = diretorio_campos / "eixo_y.npy"

        np.save(arquivo_eixo_x, eixo_x)
        np.save(arquivo_eixo_y, eixo_y)
        campos_temporais = np.lib.format.open_memmap(
            arquivo_campos,
            mode="w+",
            dtype=np.float64,
            shape=(total_eventos, *X.shape),
        )
        vmax_global_animacao = 0.0

    print(f"Calculando malhas de concentração instantâneas ...")
    for evento in range(total_eventos):
        concentracoes_xy = model.calcular_campo_instantaneo(
            evento,
            lista_puffs,
            intervalo_tempo_eventos,
            distancia_maxima_malha,
            X,
            Y,
        )

        if config.gerar_plotagens_temporais:
            campos_temporais[evento] = concentracoes_xy
            vmax_global_animacao = max(
                vmax_global_animacao,
                float(np.max(concentracoes_xy)),
            )

    if config.gerar_plotagens_temporais:
        campos_temporais.flush()
        del campos_temporais
        vmax_animacao = (
            config.vmax_animacao_efetivo
            if config.vmax_animacao_efetivo is not None
            else vmax_global_animacao
        )
        print(
            f"Vmax para animação logarítmica: {vmax_animacao:.3e} "
            f"{config.unidade}/m³"
        )

    fim_clock_1 = datetime.now()
    fim_1 = time.perf_counter()
    print(f"Fim 1 : {fim_clock_1.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tempo de processamento 1 : {fim_1 - inicio:.2f} segundos")

    if config.gerar_plotagens_temporais:
        diretorio_plotagens.mkdir(parents=True, exist_ok=True)

        for arquivo_png in diretorio_plotagens.glob("evento_*_heatmap_xy.png"):
            arquivo_png.unlink()

        campos_temporais = np.load(arquivo_campos, mmap_mode="r")
        eixo_x = np.load(arquivo_eixo_x, mmap_mode="r")
        eixo_y = np.load(arquivo_eixo_y, mmap_mode="r")

        print("Plotando mapas de calor bidimensionais ...")
        for evento, concentracoes_xy in enumerate(campos_temporais):
            plotting.plotar_heatmap_temporal(
                concentracoes_xy,
                eixo_x,
                eixo_y,
                evento,
                vmax_cores=vmax_animacao,
                cenario_id=cenario_id,
            )

        del campos_temporais
        del eixo_x
        del eixo_y

        if config.gerar_video_temporal:
            plotting.gerar_video_temporal(diretorio_plotagens)

        fim_clock_2 = datetime.now()
        fim_2 = time.perf_counter()
        print(f"Fim 2 : {fim_clock_2.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de processamento 2 : {fim_2 - inicio:.2f} segundos")


if __name__ == "__main__":
    main()
