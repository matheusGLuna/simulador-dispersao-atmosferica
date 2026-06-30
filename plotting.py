import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import PowerNorm
from pathlib import Path
from config import Config
    
config = Config()

def plotar_heatmap_xy(
    concentracoes_xyz,
    eixo_x,
    eixo_y,
    eixo_z,
    evento=None,
    exibir_maximo=True,
    campo_acumulado=False
):
    # =============================================================================
    # Plota um heatmap 2D a uma altura Z de corte desejada
    # =============================================================================

    z_corte = config.z_corte
    z_max = config.dimensao_eixo_z

    if not (0 <= z_corte <= z_max):
        raise ValueError(
            "z_corte deve estar no domínio (>= 0 e <= dimensao_eixo_z)"
        )

    i_z_corte = obter_indice_corte(eixo_z, z_corte, "z_corte", "z")
    malha_xy = concentracoes_xyz[:, :, i_z_corte]

    x_i, y_i = np.unravel_index(np.argmax(malha_xy), malha_xy.shape)
    x_max = eixo_x[x_i]
    y_max = eixo_y[y_i]

    if exibir_maximo:
        print(
            f"C(x,y,z={z_corte}) máximo no corte é de "
            f"{malha_xy[x_i, y_i]:.3e} {config.unidade}/m³"
        )
        print(f"Ocorre em x = {x_max:.2f} m e y = {y_max:.2f} m\n")

    malha_yx = malha_xy.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    render_heatmap(
        matrix=malha_yx,
        extent=[
            -config.dimensao_eixo_x,
            config.dimensao_eixo_x,
            -config.dimensao_eixo_y,
            config.dimensao_eixo_y,
        ],
        title=f"C(x,y) no plano z =  {z_corte} m",
        xlabel="x (m)",
        ylabel="y (m)",
        filename=(
            f"campo_resultante_heatmap_xy.png"
            if campo_acumulado
            else f"evento_{evento:02d}_heatmap_xy.png"
        ),
        hlines=[(0, '--', 'white')],
        campo_acumulado=campo_acumulado,
    )

def plotar_heatmap_yz(
    concentracoes_xyz,
    eixo_y,
    eixo_z,
    evento=None,
    exibir_maximo=True,
    campo_acumulado=False
):
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

    if exibir_maximo:
        print(
            f"C(y,z,x={x_corte}) máximo no corte é de "
            f"{malha_yz[y_i, z_i]:.3e} {config.unidade}/m³"
        )
        print(f"Ocorre em y = {y_max:.2f} m e z = {z_max:.2f} m\n")

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
        filename=(
            f"campo_resultante_heatmap_yz.png"
            if campo_acumulado
            else f"evento_{evento:02d}_heatmap_yz.png"
        ),
        hlines=[(config.altura_chamine, '--', 'white')],
        vlines=[(0, '--', 'white')],
        campo_acumulado=campo_acumulado,
    )

def plotar_heatmap_xz(
    concentracoes_xyz,
    eixo_x,
    eixo_z,
    evento=None,
    exibir_maximo=True,
    campo_acumulado=False
):
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

    if exibir_maximo:
        print(
            f"C(x,z,y={y_corte}) máximo no corte é de "
            f"{malha_xz[x_i, z_i]:.3e} {config.unidade}/m³"
        )
        print(f"Ocorre em x = {x_max:.2f} m e z = {z_max:.2f} m\n")

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
        filename=(
            f"campo_resultante_heatmap_xz.png"
            if campo_acumulado
            else f"evento_{evento:02d}_heatmap_xz.png"
        ),
        hlines=[(config.altura_chamine, '--', 'white')],
        campo_acumulado=campo_acumulado,
    )

def apresentar_maximos_cortes(
    concentracoes_xyz,
    eixo_x,
    eixo_y,
    eixo_z
):
    """Apresenta os máximos dos cortes habilitados para o campo acumulado."""
    print("Máximos de concentração do campo resultante:\n")

    if config.plotar_heatmap_xy:
        z_corte = config.z_corte
        i_z_corte = obter_indice_corte(eixo_z, z_corte, "z_corte", "z")
        malha_xy = concentracoes_xyz[:, :, i_z_corte]
        x_i, y_i = np.unravel_index(np.argmax(malha_xy), malha_xy.shape)
        print(
            f"C(x,y,z={z_corte}) máximo no corte é de "
            f"{malha_xy[x_i, y_i]:.3e} {config.unidade}/m³"
        )
        print(
            f"Ocorre em x = {eixo_x[x_i]:.2f} m e "
            f"y = {eixo_y[y_i]:.2f} m\n"
        )

    if config.plotar_heatmap_yz:
        x_corte = config.x_corte
        i_x_corte = int((x_corte - config.passo_x) // config.passo_x)
        malha_yz = concentracoes_xyz[i_x_corte, :, :]
        y_i, z_i = np.unravel_index(np.argmax(malha_yz), malha_yz.shape)
        print(
            f"C(y,z,x={x_corte}) máximo no corte é de "
            f"{malha_yz[y_i, z_i]:.3e} {config.unidade}/m³"
        )
        print(
            f"Ocorre em y = {eixo_y[y_i]:.2f} m e "
            f"z = {eixo_z[z_i]:.2f} m\n"
        )

    if config.plotar_heatmap_xz:
        y_corte = config.y_corte
        i_y_corte = int(
            (y_corte + config.dimensao_eixo_y) // config.passo_y
        )
        malha_xz = concentracoes_xyz[:, i_y_corte, :]
        x_i, z_i = np.unravel_index(np.argmax(malha_xz), malha_xz.shape)
        print(
            f"C(x,z,y={y_corte}) máximo no corte é de "
            f"{malha_xz[x_i, z_i]:.3e} {config.unidade}/m³"
        )
        print(
            f"Ocorre em x = {eixo_x[x_i]:.2f} m e "
            f"z = {eixo_z[z_i]:.2f} m\n"
        )

def plotar_cortes_acumulados(
    concentracoes_xyz,
    eixo_x,
    eixo_y,
    eixo_z
):
    """Plota e mantém abertas somente as figuras do campo acumulado."""
    if config.plotar_heatmap_xy:
        plotar_heatmap_xy(
            concentracoes_xyz,
            eixo_x,
            eixo_y,
            eixo_z,
            exibir_maximo=False,
            campo_acumulado=True
        )

    if config.plotar_heatmap_yz:
        plotar_heatmap_yz(
            concentracoes_xyz,
            eixo_y,
            eixo_z,
            exibir_maximo=False,
            campo_acumulado=True
        )

    if config.plotar_heatmap_xz:
        plotar_heatmap_xz(
            concentracoes_xyz,
            eixo_x,
            eixo_z,
            exibir_maximo=False,
            campo_acumulado=True
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
):
    figura, eixo = plt.subplots(figsize=(12, 6), dpi=150)
    imagem = eixo.imshow(
        matrix,
        origin='lower',
        extent=extent,
        aspect=aspect,
        norm=PowerNorm(config.gamma),
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

    cbar = figura.colorbar(imagem, ax=eixo, orientation='horizontal')
    cbar.set_label(f"Concentração em {config.unidade}/m³")

    if campo_acumulado:
        output_dir = (
            Path(config.diretorio_dados_acumulados)
            / f"s{config.seed}"
            / config.diretorio_plotagens_acumuladas
        )
    else:
        output_dir = (
            Path(config.diretorio_dados_parciais)
            / f"s{config.seed}"
            / config.diretorio_plotagens_parciais
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        figura.tight_layout()
        figura.savefig(output_dir / filename, dpi=150)
    except Exception as e:
        print(f"Falha ao salvar {filename}: {e}")
    finally:
        if not campo_acumulado:
            plt.close(figura)

def show_heatmap():
    plt.show()

def obter_indice_corte(eixo, valor_corte, nome_corte, nome_eixo):
    indices = np.where(np.isclose(eixo, valor_corte))[0]

    if len(indices) == 0:
        valores_disponiveis = ", ".join(f"{valor:.2f}" for valor in eixo)
        raise ValueError(
            f"{nome_corte}={valor_corte} não corresponde a nenhum ponto do "
            f"eixo {nome_eixo}. Valores disponíveis: {valores_disponiveis}"
        )

    return int(indices[0])
