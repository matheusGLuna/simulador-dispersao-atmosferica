import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import PowerNorm
from pathlib import Path
from config import Config
    
config = Config()

def plotar_heatmap_xy(concentracoes_xyz, eixo_x, eixo_y, evento):
    # =============================================================================
    # Plota um heatmap 2D a uma altura Z de corte desejada
    # =============================================================================

    z_corte = config.z_corte
    z_step = config.passo_z
    z_max = config.dimensao_eixo_z

    if not (0 <= z_corte <= z_max):
        raise ValueError(
            "z_corte deve estar no domínio (>= 0 e <= dimensao_eixo_z)"
        )

    if z_corte % z_step != 0:
        raise ValueError(
            "z_corte deve ser múltiplo inteiro de passo_z (ou zero)"
        )

    i_z_corte = int(z_corte // z_step)
    malha_xy = concentracoes_xyz[:, :, i_z_corte]

    x_i, y_i = np.unravel_index(np.argmax(malha_xy), malha_xy.shape)
    x_max = eixo_x[x_i]
    y_max = eixo_y[y_i]

    print(
        f"C(x,y,z={z_corte}) máximo no corte é de {malha_xy[x_i, y_i]:.3e} "
        f"{config.unidade}/m³"
    )
    print(f"Ocorre em x = {x_max:.2f} m e y= {y_max:.2f}m\n")

    malha_yx = malha_xy.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    render_heatmap(
        matrix=malha_yx,
        extent=[
            config.passo_x,
            config.dimensao_eixo_x,
            -config.dimensao_eixo_y,
            config.dimensao_eixo_y,
        ],
        title=f"C(x,y) no plano z =  {z_corte} m",
        xlabel="x (m)",
        ylabel="y (m)",
        filename=f"heatmap_xy_z{z_corte}.e{evento}.png",
        hlines=[(0, '--', 'white')],
    )

def plotar_heatmap_yz(concentracoes_xyz, eixo_y, eixo_z, evento):
    # =============================================================================
    # Plota um heatmap 2D a uma distancia y de corte desejada
    # =============================================================================
    if concentracoes_xyz is None:
        raise ValueError("heatmap 2D tem como pré req a criação do meshgrid 3D")

    x_corte = config.x_corte
    x_step = config.passo_x
    x_max = config.dimensao_eixo_x

    if not (x_step <= x_corte <= x_max):
        raise ValueError(
            "x_corte deve estar no domínio (>= passo_x e <= dimensao_eixo_x)"
        )

    if x_corte % x_step != 0:
        raise ValueError("x_corte deve ser múltiplo inteiro de passo_x")

    i_x_corte = int((x_corte - x_step) // x_step)
    malha_yz = concentracoes_xyz[i_x_corte, :, :]

    y_i, z_i = np.unravel_index(np.argmax(malha_yz), malha_yz.shape)
    y_max = eixo_y[y_i]
    z_max = eixo_z[z_i]

    print(
        f"C(y,z,x={x_corte}) máximo no corte é de {malha_yz[y_i, z_i]:.3e} "
        f"{config.unidade}/m³"
    )
    print(f"Ocorre em y = {y_max:.2f} m e z= {z_max:.2f}m\n")

    malha_zy = malha_yz.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    render_heatmap(
        matrix=malha_zy,
        extent=[
            -config.dimensao_eixo_y,
            config.dimensao_eixo_y,
            0,
            config.dimensao_eixo_z,
        ],
        title=f"C(y,z) no plano x = {x_corte} m",
        xlabel="y (m)",
        ylabel="z (m)",
        filename=f"heatmap_yz_x{x_corte}.e{evento}.png",
        hlines=[(config.altura_chamine, '--', 'white')],
        vlines=[(0, '--', 'white')],
    )

def plotar_heatmap_xz(concentracoes_xyz, eixo_x, eixo_z, evento):
    # =============================================================================
    # Plota um heatmap 2D a uma distancia y de corte desejada
    # =============================================================================
    if concentracoes_xyz is None:
        raise ValueError("heatmap 2D tem como pré req a criação do meshgrid 3D")

    y_corte = config.y_corte
    y_step = config.passo_y
    y_max = config.dimensao_eixo_y

    if not (-y_max <= y_corte <= y_max):
        raise ValueError(
            "y_corte deve satisfazer: -dimensao_eixo_y <= y_corte <= dimensao_eixo_y"
        )

    if y_corte % y_step != 0:
        raise ValueError("y_corte deve ser múltiplo inteiro de passo_y (ou zero)")

    i_y_corte = int((y_corte + y_max) // y_step)
    malha_xz = concentracoes_xyz[:, i_y_corte, :]

    x_i, z_i = np.unravel_index(np.argmax(malha_xz), malha_xz.shape)
    x_max = eixo_x[x_i]
    z_max = eixo_z[z_i]

    print(
        f"C(x,z,y={y_corte}) máximo no corte é de {malha_xz[x_i, z_i]:.3e} "
        f"{config.unidade}/m³"
    )
    print(f"Ocorre em x = {x_max:.2f} m e z= {z_max:.2f}m\n")

    malha_zx = malha_xz.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    render_heatmap(
        matrix=malha_zx,
        extent=[
            config.passo_x,
            config.dimensao_eixo_x,
            0,
            config.dimensao_eixo_z,
        ],
        title=f"C(x,z) no plano y = {y_corte} m",
        xlabel="x (m)",
        ylabel="z (m)",
        filename=f"heatmap_xz_y{y_corte}.e{evento}.png",
        aspect=4,
        hlines=[(config.altura_chamine, '--', 'white')],
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
):
    plt.figure(figsize=(12, 6), dpi=150)
    plt.imshow(
        matrix,
        origin='lower',
        extent=extent,
        aspect=aspect,
        norm=PowerNorm(config.gamma),
    )
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if vlines is not None:
        for position, style, color in vlines:
            plt.axvline(x=position, linestyle=style, color=color)

    if hlines is not None:
        for position, style, color in hlines:
            plt.axhline(y=position, linestyle=style, color=color)

    cbar = plt.colorbar(orientation='horizontal')
    cbar.set_label(f"Concentração em {config.unidade}/m³")

    output_dir = (
        Path("resultados_plotados")
        / f"s{config.seed}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        plt.tight_layout()
        plt.savefig(output_dir/filename, dpi=150)
    except Exception as e:
        print(f"Falha ao salvar {filename}: {e}")

def show_heatmap():
    plt.show()