import math
import numpy as npy
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

CONFIG = {

    "taxa_emissao_fonte": 1500,     # [Ci/segundo]
    "converter_ci_bq": True,

    "altura_chamine": 100,          # [m]
    "velocidade_vento": 5,          # [m/segundo]
    "classe_estabilidade": "D",     # classe estabilidade atmosférica
    "terreno":"R",                  # R para rural, U para urbano

    "gerar_meshgrid_xyz": True,
    "dimensao_eixo_x": 20000,       # [m] inteiro >= 1 e multiplo de passo_x
    "dimensao_eixo_y": 2500,        # [m] inteiro >= 0 e multiplo de passo_y
    "dimensao_eixo_z": 1000,        # [m] inteiro >= 0 e multiplo de passo_z
    "passo_x": 50,                  # [m] inteiro >= 1
    "passo_y": 25,                  # [m] inteiro >= 1
    "passo_z": 10,                  # [m] inteiro >= 1
    "limite_pontos": 12_500_000,    # limite de pontos simulados (sugestão: 10^6 a 10^8)

    "calcular_ponto_especifico": False,
    "x_calculo": 2000,
    "y_calculo": 0,
    "z_calculo": 100,

    "plotar_heatmap_xy": True,
    "z_corte": 0,                   # altura z do corte no plano xy
                                    # multiplos de passo_z (ou zero)
                                    # Obs.: zero para nivel do solo

    "plotar_heatmap_yz": True,
    "x_corte": 10000,               # distancia x do corte no plano yz
                                    # multiplos de passo_x

    "plotar_heatmap_xz": True,
    "y_corte": 250,                 # lateralidade y do corte no plano xz
                                    # multiplos de passo_y

    "gamma": 0.4,                   # 0.3 a 0.9
                                    # proximo a 0.3 -> realça frios (baixas concentrações)
                                    # proximo a 0.9 -> realça quentes (altas concentrações)

}

def gerar_meshgrid_xyz(x_max, x_step, y_max, y_step, z_max, z_step):

    num_x = int(x_max / x_step)
    num_y = int(2*y_max/y_step) + 1
    num_z = int(z_max / z_step) + 1

    total_pontos = num_x * num_y * num_z

    if total_pontos > CONFIG["limite_pontos"]:
        errorString = (
            f"Essa modelagem resultaria em {total_pontos} pontos, acima do "
            f"limite parametrizado de {CONFIG['limite_pontos']}.\n"
            "Aumente o limite parametrizado ou os intervalos (passos) entre pontos"
        )
        raise ValueError(errorString)
    else:
        print(f"{total_pontos} pontos configurados para modelagem")

    x_vals = npy.linspace(x_step, x_max, num_x)
    # parte de x_step (e não de zero) para evitar incertezas na boca da chaminé
    y_vals = npy.linspace(-y_max, y_max, num_y)
    z_vals = npy.linspace(0, z_max, num_z)

    X, Y, Z = npy.meshgrid(x_vals, y_vals, z_vals, indexing='ij')

    return calcular_concentracao(X, Y, Z), x_vals, y_vals, z_vals

def calcular_concentracao(X, Y, Z):

    sigma_y = calcular_sigma_y(X, CONFIG["classe_estabilidade"], CONFIG["terreno"])
    sigma_z = calcular_sigma_z(X, CONFIG["classe_estabilidade"], CONFIG["terreno"])

    fator = CONFIG["taxa_emissao_fonte"] / (
        2*math.pi * CONFIG["velocidade_vento"] * sigma_y * sigma_z
    )

    expo1 = -(
    (Y**2)/(2*(sigma_y**2)) +
    ((Z - CONFIG["altura_chamine"])**2)/(2*(sigma_z**2))
    )

    expo2 = -(
        (Y**2)/(2*(sigma_y**2)) +
        ((Z + CONFIG["altura_chamine"])**2)/(2*(sigma_z**2))
    )

    return (fator*(npy.exp(expo1) + npy.exp(expo2)))

def calcular_sigma_y(x, classe, terreno):

    classe = classe.upper()
    terreno = terreno.upper()

    if terreno == 'R':
        if classe == 'A':
            return 0.22 * x * (1 + 0.0001 * x)**(-0.5)
        elif classe == 'B':
            return 0.16 * x * (1 + 0.0001 * x)**(-0.5)
        elif classe == 'C':
            return 0.11 * x * (1 + 0.0001 * x)**(-0.5)
        elif classe == 'D':
            return 0.08 * x * (1 + 0.0001 * x)**(-0.5)
        elif classe == 'E':
            return 0.06 * x * (1 + 0.0001 * x)**(-0.5)
        elif classe == 'F':
            return 0.04 * x * (1 + 0.0001 * x)**(-0.5)
        else:
            raise ValueError("Classe de estabilidade inválida")

    elif terreno == 'U':
        if classe in ['A', 'B']:
            return 0.32 * x * (1 + 0.0004 * x)**(-0.5)
        elif classe == 'C':
            return 0.22 * x * (1 + 0.0004 * x)**(-0.5)
        elif classe == 'D':
            return 0.16 * x * (1 + 0.0004 * x)**(-0.5)
        elif classe in ['E', 'F']:
            return 0.11 * x * (1 + 0.0004 * x)**(-0.5)
        else:
            raise ValueError("Classe de estabilidade inválida")

    else:
        raise ValueError("Terreno inválido: use 'R' (rural) ou 'U' (urbano)")

def calcular_sigma_z(x, classe, terreno):

    classe = classe.upper()
    terreno = terreno.upper()

    if terreno == 'R':  # Rural
        if classe == 'A':
            return 0.20 * x
        elif classe == 'B':
            return 0.12 * x
        elif classe == 'C':
            return 0.08 * x * (1 + 0.0002 * x)**(-0.5)
        elif classe == 'D':
            return 0.06 * x * (1 + 0.0015 * x)**(-0.5)
        elif classe == 'E':
            return 0.03 * x * (1 + 0.0003 * x)**(-1.0)
        elif classe == 'F':
            return 0.016 * x * (1 + 0.0003 * x)**(-1.0)
        else:
            raise ValueError("Classe de estabilidade inválida")

    elif terreno == 'U':  # Urbano
        if classe in ['A', 'B']:
            return 0.24 * x * (1 + 0.001 * x)**(0.5)
        elif classe == 'C':
            return 0.20 * x
        elif classe == 'D':
            return 0.14 * x * (1 + 0.0003 * x)**(-0.5)
        elif classe in ['E', 'F']:
            return 0.08 * x * (1 + 0.0015 * x)**(-0.5)
        else:
            raise ValueError("Classe de estabilidade inválida")

    else:
        raise ValueError("Terreno inválido: use 'R' (rural) ou 'U' (urbano)")

# =========================
# EXECUCAO
# =========================

unidade = "Ci"

if CONFIG["converter_ci_bq"]:
# ============================================================================
# Converte unidade base da taxa de emissao da fonte de Ci para Bq
# ============================================================================
    unidade = "Bq"
    CONFIG["taxa_emissao_fonte"] = CONFIG["taxa_emissao_fonte"]*3.7e10

if CONFIG["calcular_ponto_especifico"]:
# ============================================================================
# Calcula concentração C(x=a,y=b,z=c) apenas no ponto particular informado
# ============================================================================

    x_particular = abs(CONFIG["x_calculo"])
    y_particular = abs(CONFIG["y_calculo"])
    z_particular= abs(CONFIG["z_calculo"])

    concentracao = calcular_concentracao(x_particular,
                                         y_particular,
                                         z_particular)

    print(f"No ponto solicitado: "
          f"C({x_particular},{y_particular},{z_particular}) = "
          f"{concentracao:.3e} {unidade}/m³\n")

if CONFIG["gerar_meshgrid_xyz"]:
# ============================================================================
# Gera meshgrid 3d de concentrações C(x,y,z) para todos os pontos no espaço
# ============================================================================

    concentracoes_xyz, eixo_x, eixo_y, eixo_z = gerar_meshgrid_xyz(
        CONFIG["dimensao_eixo_x"],
        CONFIG["passo_x"],
        CONFIG["dimensao_eixo_y"],
        CONFIG["passo_y"],
        CONFIG["dimensao_eixo_z"],
        CONFIG["passo_z"]
    )

    print(f"meshgrid de concentrações C(x,y,z) modelado com sucesso\n")

if CONFIG["plotar_heatmap_xy"]:
# =============================================================================
# Plota um heatmap 2D a uma altura Z de corte desejada
# =============================================================================

    if not CONFIG["gerar_meshgrid_xyz"]:
      raise ValueError("heatmap 2D tem como pré req a criação do meshgrid 3D")

    z_corte = CONFIG["z_corte"]
    z_step = CONFIG["passo_z"]
    z_max = CONFIG["dimensao_eixo_z"]

    if not (0 <= z_corte <= z_max):
        raise ValueError("z_corte deve estar no domínio (>= 0 e <= dimensao_eixo_z)")

    if z_corte % z_step != 0:
        raise ValueError("z_corte deve ser múltiplo inteiro de passo_z (ou zero)")

    i_z_corte = z_corte // z_step

    malha_xy = concentracoes_xyz[:, :, i_z_corte]

    x_i, y_i = npy.unravel_index(npy.argmax(malha_xy), malha_xy.shape)

    x_max = eixo_x[x_i]
    y_max = eixo_y[y_i]

    print(f"C(x,y,z={z_corte}) máximo no corte é de {malha_xy[x_i, y_i]:.3e} {unidade}/m³")
    print(f"Ocorre em x = {x_max:.2f} m e y= {y_max:.2f}m\n")

    malha_yx = malha_xy.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    plt.figure(figsize=(12, 6), dpi=150)
    plt.imshow(
        malha_yx,
        origin='lower',
        extent=[
                CONFIG["passo_x"],
                CONFIG["dimensao_eixo_x"],
                -CONFIG["dimensao_eixo_y"],
                CONFIG["dimensao_eixo_y"]
        ],
        aspect=1,
        norm=PowerNorm(CONFIG["gamma"])
    )

    heatmap_title = f"C(x,y) no plano z =  {z_corte} m"
    plt.title(heatmap_title)
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.axhline(y=0, linestyle='--', color='white')

    cbar = plt.colorbar(orientation='horizontal')
    cbar.set_label(f"Concentração em {unidade}/m³")

if CONFIG["plotar_heatmap_yz"]:
# =============================================================================
# Plota um heatmap 2D a uma distancia y de corte desejada
# =============================================================================

    if not CONFIG["gerar_meshgrid_xyz"]:
      raise ValueError("heatmap 2D tem como pré req a criação do meshgrid 3D")

    x_corte = CONFIG["x_corte"]
    x_step = CONFIG["passo_x"]
    x_max = CONFIG["dimensao_eixo_x"]

    if not (x_step <= x_corte <= x_max):
        raise ValueError("x_corte deve estar no domínio (>= passo_x e <= dimensao_eixo_x)")

    if x_corte % x_step != 0:
        raise ValueError("x_corte deve ser múltiplo inteiro de passo_x")

    i_x_corte = (x_corte - x_step) // x_step

    malha_yz = concentracoes_xyz[i_x_corte, :, :]

    y_i, z_i = npy.unravel_index(npy.argmax(malha_yz), malha_yz.shape)

    y_max = eixo_y[y_i]
    z_max = eixo_z[z_i]

    print(f"C(y,z,x={x_corte}) máximo no corte é de {malha_yz[y_i, z_i]:.3e} {unidade}/m³")
    print(f"Ocorre em y = {y_max:.2f} m e z= {z_max:.2f}m\n")

    malha_zy = malha_yz.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    plt.figure(figsize=(12, 6), dpi=150)
    plt.imshow(
        malha_zy,
        origin='lower',
        extent=[
                -CONFIG["dimensao_eixo_y"],
                CONFIG["dimensao_eixo_y"],
                0,
                CONFIG["dimensao_eixo_z"]
        ],
        aspect=1,
        norm=PowerNorm(CONFIG["gamma"])
    )

    heatmap_title = f"C(y,z) no plano x = {x_corte} m"
    plt.title(heatmap_title)
    plt.xlabel("y (m)")
    plt.ylabel("z (m)")
    plt.axvline(x=0, linestyle='--', color='white')
    plt.axhline(y=CONFIG["altura_chamine"], linestyle='--', color='white')

    cbar = plt.colorbar(orientation='horizontal')
    cbar.set_label(f"Concentração em {unidade}/m³")

if CONFIG["plotar_heatmap_xz"]:
# =============================================================================
# Plota um heatmap 2D a uma distancia y de corte desejada
# =============================================================================

    if not CONFIG["gerar_meshgrid_xyz"]:
      raise ValueError("heatmap 2D tem como pré req a criação do meshgrid 3D")

    y_corte = CONFIG["y_corte"]
    y_step = CONFIG["passo_y"]
    y_max = CONFIG["dimensao_eixo_y"]

    if not (-y_max <= y_corte <= y_max):
        raise ValueError("y_corte deve satisfazer: -dimensao_eixo_y <= y_corte <= dimensao_eixo_y")

    if y_corte % y_step != 0:
        raise ValueError("y_corte deve ser múltiplo inteiro de passo_y (ou zero)")

    i_y_corte = (y_corte + y_max) // y_step

    malha_xz = concentracoes_xyz[:, i_y_corte, :]

    x_i, z_i = npy.unravel_index(npy.argmax(malha_xz), malha_xz.shape)

    x_max = eixo_x[x_i]
    z_max = eixo_z[z_i]

    print(f"C(x,z,y={y_corte}) máximo no corte é de {malha_xz[x_i, z_i]:.3e} {unidade}/m³")
    print(f"Ocorre em x = {x_max:.2f} m e z= {z_max:.2f}m\n")

    malha_zx = malha_xz.transpose()
    # Transpondo para representação mais adequada na plotagem do inshow

    plt.figure(figsize=(12, 6), dpi=150)
    plt.imshow(
        malha_zx,
        origin='lower',
        extent=[
                CONFIG["passo_x"],
                CONFIG["dimensao_eixo_x"],
                0,
                CONFIG["dimensao_eixo_z"]
        ],
        aspect=4,
        norm=PowerNorm(CONFIG["gamma"])
    )

    heatmap_title = f"C(x,z) no plano y = {y_corte} m"
    plt.title(heatmap_title)
    plt.xlabel("x (m)")
    plt.ylabel("z (m)")
    plt.axhline(y=CONFIG["altura_chamine"], linestyle='--', color='white')

    cbar = plt.colorbar(orientation='horizontal')
    cbar.set_label(f"Concentração em {unidade}/m³")