from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm, PowerNorm

from config import Config


config = Config()


def plotar_heatmap_xy(
    concentracoes_xy,
    eixo_x,
    eixo_y,
    evento=None,
    campo_acumulado=False,
    vmax_referencia=None,
    cenario_id=None,
):
    """Plota a concentração no plano XY, ao nível do solo (z = 0)."""
    matrix = concentracoes_xy.transpose()
    extent = [eixo_x[0], eixo_x[-1], eixo_y[0], eixo_y[-1]]
    largura_malha = eixo_x[-1] - eixo_x[0]
    altura_malha = eixo_y[-1] - eixo_y[0]
    proporcao_malha = largura_malha / altura_malha
    lado_maior = 10

    if proporcao_malha >= 1:
        largura_figura = lado_maior
        altura_mapa = lado_maior / proporcao_malha
    else:
        largura_figura = lado_maior * proporcao_malha
        altura_mapa = lado_maior

    altura_figura = altura_mapa + 1.2
    filename = (
        "campo_resultante_heatmap_xy.png"
        if campo_acumulado
        else f"evento_{evento:02d}_heatmap_xy.png"
    )

    figura, eixo = plt.subplots(
        figsize=(largura_figura, altura_figura),
        dpi=150,
        layout="constrained",
    )
    imagem = eixo.imshow(
        matrix,
        origin="lower",
        extent=extent,
        aspect=1,
        norm=obter_normalizacao(vmax_referencia),
    )
    eixo.set_title("C(x,y) ao nível do solo (z = 0 m)")
    eixo.set_xlabel("x (m)")
    eixo.set_ylabel("y (m)")
    eixo.axhline(y=0, linestyle="--", color="white", linewidth=0.5)
    eixo.axvline(x=0, linestyle="--", color="white", linewidth=0.5)

    if config.usar_escala_logaritmica and config.exibir_contornos_logaritmicos:
        niveis = np.geomspace(
            config.vmin_logaritmico_efetivo,
            vmax_referencia,
            config.quantidade_contornos_logaritmicos,
        )
        eixo.contour(
            matrix,
            levels=niveis,
            origin="lower",
            extent=extent,
            colors="white",
            linewidths=0.5,
        )

    cbar = figura.colorbar(
        imagem,
        ax=eixo,
        orientation="horizontal",
        fraction=0.05,
        pad=0.10,
    )
    cbar.set_label(f"Concentração em {config.unidade}/m³")

    identificador_cenario = cenario_id or f"cenario{config.seed}"

    if campo_acumulado:
        output_dir = (
            Path(config.diretorio_dados_acumulados)
            / identificador_cenario
            / config.diretorio_plotagens_acumuladas
        )
    else:
        output_dir = (
            Path(config.diretorio_dados_parciais)
            / identificador_cenario
            / config.diretorio_plotagens_parciais
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        figura.savefig(output_dir / filename, dpi=150)
    except Exception as error:
        print(f"Falha ao salvar {filename}: {error}")
    finally:
        if not campo_acumulado:
            plt.close(figura)


def show_heatmap():
    plt.show()


def obter_normalizacao(vmax_referencia):
    """Retorna a normalização de cores configurada para os heatmaps."""
    if not config.usar_escala_logaritmica:
        return PowerNorm(config.gamma)

    if vmax_referencia is None:
        raise ValueError(
            "A escala logarítmica requer um vmax de referência do campo acumulado"
        )

    vmin_logaritmico = config.vmin_logaritmico_efetivo

    if vmin_logaritmico <= 0:
        raise ValueError("vmin_logaritmico deve ser maior que zero")

    if vmax_referencia <= vmin_logaritmico:
        raise ValueError(
            "O vmax de referência deve ser maior que vmin_logaritmico para "
            "usar escala logarítmica"
        )

    if (
        config.exibir_contornos_logaritmicos
        and config.quantidade_contornos_logaritmicos < 2
    ):
        raise ValueError(
            "quantidade_contornos_logaritmicos deve ser pelo menos 2"
        )

    return LogNorm(vmin=vmin_logaritmico, vmax=vmax_referencia)
