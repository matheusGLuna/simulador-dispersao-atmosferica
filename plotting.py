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
    exibir_maximo=True,
    campo_acumulado=False,
    vmax_referencia=None,
):
    """Plota a concentração no plano XY, ao nível do solo (z = 0)."""
    x_i, y_i = np.unravel_index(np.argmax(concentracoes_xy), concentracoes_xy.shape)

    if exibir_maximo:
        print(
            f"C(x,y,z=0) máxima é de "
            f"{concentracoes_xy[x_i, y_i]:.3e} {config.unidade}/m³"
        )
        print(f"Ocorre em x = {eixo_x[x_i]:.2f} m e y = {eixo_y[y_i]:.2f} m\n")

    render_heatmap(
        matrix=concentracoes_xy.transpose(),
        extent=[
            eixo_x[0],
            eixo_x[-1],
            eixo_y[0],
            eixo_y[-1],
        ],
        title="C(x,y) ao nível do solo (z = 0 m)",
        xlabel="x (m)",
        ylabel="y (m)",
        filename=(
            "campo_resultante_heatmap_xy.png"
            if campo_acumulado
            else f"evento_{evento:02d}_heatmap_xy.png"
        ),
        hlines=[(0, "--", "white")],
        campo_acumulado=campo_acumulado,
        vmax_referencia=vmax_referencia,
    )


def apresentar_maximo_campo(concentracoes_xy, eixo_x, eixo_y):
    """Apresenta o ponto de maior concentração do campo acumulado no solo."""
    print("Máximo de concentração do campo resultante:\n")
    x_i, y_i = np.unravel_index(np.argmax(concentracoes_xy), concentracoes_xy.shape)
    print(
        f"C(x,y,z=0) máxima é de "
        f"{concentracoes_xy[x_i, y_i]:.3e} {config.unidade}/m³"
    )
    print(f"Ocorre em x = {eixo_x[x_i]:.2f} m e y = {eixo_y[y_i]:.2f} m\n")


def plotar_campo_acumulado(concentracoes_xy, eixo_x, eixo_y, vmax_referencia):
    """Gera e mantém aberta a figura do campo acumulado no plano XY."""
    plotar_heatmap_xy(
        concentracoes_xy,
        eixo_x,
        eixo_y,
        exibir_maximo=False,
        campo_acumulado=True,
        vmax_referencia=vmax_referencia,
    )


def render_heatmap(
    matrix,
    extent,
    title,
    xlabel,
    ylabel,
    filename,
    aspect=1,
    hlines=None,
    vlines=None,
    campo_acumulado=False,
    vmax_referencia=None,
):
    figura, eixo = plt.subplots(figsize=(12, 6), dpi=150)
    imagem = eixo.imshow(
        matrix,
        origin="lower",
        extent=extent,
        aspect=aspect,
        norm=obter_normalizacao(vmax_referencia),
    )
    eixo.set_title(title)
    eixo.set_xlabel(xlabel)
    eixo.set_ylabel(ylabel)

    if vlines is not None:
        for position, style, color in vlines:
            eixo.axvline(x=position, linestyle=style, color=color)

    if hlines is not None:
        for position, style, color in hlines:
            eixo.axhline(y=position, linestyle=style, color=color)

    if config.usar_escala_logaritmica and config.exibir_contornos_logaritmicos:
        niveis = np.geomspace(
            config.vmin_logaritmico,
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

    cbar = figura.colorbar(imagem, ax=eixo, orientation="horizontal")
    cbar.set_label(f"Concentração em {config.unidade}/m³")

    if campo_acumulado:
        output_dir = (
            Path(config.diretorio_dados_acumulados)
            / f"cenario{config.seed}"
            / config.diretorio_plotagens_acumuladas
        )
    else:
        output_dir = (
            Path(config.diretorio_dados_parciais)
            / f"cenario{config.seed}"
            / config.diretorio_plotagens_parciais
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        figura.tight_layout()
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

    if config.vmin_logaritmico <= 0:
        raise ValueError("vmin_logaritmico deve ser maior que zero")

    if vmax_referencia <= config.vmin_logaritmico:
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

    return LogNorm(vmin=config.vmin_logaritmico, vmax=vmax_referencia)
