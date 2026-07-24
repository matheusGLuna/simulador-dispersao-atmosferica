from pathlib import Path
import shutil
import subprocess

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm, PowerNorm

from config import Config


config = Config()


def criar_layout_mapa_com_barra(eixo_x, eixo_y):
    """Cria eixos de mapa e barra horizontal com a mesma largura útil."""
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

    figura = plt.figure(
        figsize=(largura_figura, altura_mapa + 1.6),
        dpi=150,
        layout="constrained",
    )
    grade = figura.add_gridspec(
        2,
        1,
        height_ratios=[altura_mapa, 0.35],
    )
    eixo_mapa = figura.add_subplot(grade[0])
    eixo_barra = figura.add_subplot(grade[1])
    return figura, eixo_mapa, eixo_barra


def plotar_heatmap_temporal(
    concentracoes_xy,
    eixo_x,
    eixo_y,
    evento,
    vmax_cores,
    cenario_id,
):
    """Salva o heatmap XY de um frame temporal ao nível do solo."""
    matrix = concentracoes_xy.transpose()
    extent = [eixo_x[0], eixo_x[-1], eixo_y[0], eixo_y[-1]]
    figura, eixo, eixo_barra = criar_layout_mapa_com_barra(eixo_x, eixo_y)
    imagem = eixo.imshow(
        matrix,
        origin="lower",
        extent=extent,
        aspect=1,
        norm=obter_normalizacao(vmax_cores),
    )
    eixo.set_title("C(x,y) ao nível do solo (z = 0 m)")
    eixo.set_xlabel("x (m)")
    eixo.set_ylabel("y (m)")
    eixo.axhline(y=0, linestyle="--", color="white", linewidth=0.5)
    eixo.axvline(x=0, linestyle="--", color="white", linewidth=0.5)

    if config.usar_escala_logaritmica and config.exibir_contornos_logaritmicos:
        niveis = np.geomspace(
            config.vmin_logaritmico_efetivo,
            vmax_cores,
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
        cax=eixo_barra,
        orientation="horizontal",
    )
    cbar.set_label(f"Concentração em {config.unidade}/m³")

    diretorio_saida = (
        Path(config.diretorio_dados_parciais)
        / cenario_id
        / config.diretorio_plotagens_parciais
    )
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"evento_{evento:02d}_heatmap_xy.png"

    try:
        figura.savefig(diretorio_saida / nome_arquivo, dpi=150)
    except Exception as error:
        print(f"Falha ao salvar {nome_arquivo}: {error}")
    finally:
        plt.close(figura)


def gerar_video_temporal(diretorio_plotagens, fps=10):
    """Gera o MP4 da sequência de PNGs temporais usando o FFmpeg disponível."""
    diretorio_plotagens = Path(diretorio_plotagens)
    imagens_temporais = list(
        diretorio_plotagens.glob("evento_*_heatmap_xy.png")
    )

    if not imagens_temporais:
        print(
            "Nenhuma imagem temporal foi encontrada; o vídeo temporal não foi gerado."
        )
        return False

    arquivo_video = diretorio_plotagens / "evolucao_temporal.mp4"
    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg is None:
        print("FFmpeg não encontrado; o vídeo temporal não foi gerado.")
        return False

    comando_ffmpeg = [
        ffmpeg,
        "-y",
        "-framerate",
        str(fps),
        "-start_number",
        "1",
        "-i",
        str(diretorio_plotagens / "evento_%02d_heatmap_xy.png"),
        "-vf",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(arquivo_video),
    ]

    try:
        subprocess.run(comando_ffmpeg, check=True)
    except subprocess.CalledProcessError as error:
        print(f"Falha ao gerar o vídeo temporal: {error}")
        return False

    print(f"Vídeo temporal salvo em: {arquivo_video}")
    return True


def plotar_heatmap_dosimetria(
    campo_dose_xy,
    eixo_x,
    eixo_y,
    titulo,
    nome_arquivo,
    vmin_cores,
    vmax_cores,
    cenario_id,
):
    """Salva um mapa XY de dose com a normalização configurada."""
    matrix = campo_dose_xy.transpose()
    extent = [eixo_x[0], eixo_x[-1], eixo_y[0], eixo_y[-1]]
    figura, eixo, eixo_barra = criar_layout_mapa_com_barra(eixo_x, eixo_y)
    imagem = eixo.imshow(
        matrix,
        origin="lower",
        extent=extent,
        aspect=1,
        norm=obter_normalizacao(vmax_cores, vmin_cores),
    )
    eixo.set_title(titulo)
    eixo.set_xlabel("x (m)")
    eixo.set_ylabel("y (m)")
    eixo.axhline(y=0, linestyle="--", color="white", linewidth=0.5)
    eixo.axvline(x=0, linestyle="--", color="white", linewidth=0.5)

    if config.usar_escala_logaritmica and config.exibir_contornos_logaritmicos:
        niveis = np.geomspace(
            vmin_cores,
            vmax_cores,
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
        cax=eixo_barra,
        orientation="horizontal",
    )
    cbar.set_label("Dose efetiva (Sv)")

    diretorio_saida = (
        Path(config.diretorio_dados_parciais)
        / cenario_id
        / config.diretorio_plotagens_dosimetria
    )
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    try:
        figura.savefig(diretorio_saida / nome_arquivo, dpi=150)
    except Exception as error:
        print(f"Falha ao salvar {nome_arquivo}: {error}")
    finally:
        plt.close(figura)


def obter_normalizacao(vmax_cores, vmin_cores=None):
    """Retorna a normalização de cores dos frames temporais."""
    if not config.usar_escala_logaritmica:
        return PowerNorm(config.gamma)

    if vmax_cores is None:
        raise ValueError(
            "A escala logarítmica requer um vmax de cores para a animação"
        )

    vmin_logaritmico = (
        config.vmin_logaritmico_efetivo
        if vmin_cores is None
        else vmin_cores
    )

    if vmin_logaritmico <= 0:
        raise ValueError("vmin_logaritmico deve ser maior que zero")

    if vmax_cores <= vmin_logaritmico:
        raise ValueError(
            "O vmax de cores deve ser maior que vmin_logaritmico para "
            "usar escala logarítmica"
        )

    if (
        config.exibir_contornos_logaritmicos
        and config.quantidade_contornos_logaritmicos < 2
    ):
        raise ValueError(
            "quantidade_contornos_logaritmicos deve ser pelo menos 2"
        )

    return LogNorm(vmin=vmin_logaritmico, vmax=vmax_cores)
