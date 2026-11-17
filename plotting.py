from pathlib import Path
import shutil
import subprocess
import textwrap

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm, PowerNorm

from config import Config


config = Config()


def obter_niveis_contorno_logaritmicos(vmin, vmax):
    """Inclui o limiar exato e as décadas seguintes, sem incluir o máximo."""
    if vmax <= vmin:
        return np.empty(0)

    expoentes = np.arange(
        np.floor(np.log10(vmin)),
        np.ceil(np.log10(vmax)) + 1,
    )
    decadas = 10.0 ** expoentes
    decadas = decadas[
        (decadas > vmin)
        & (decadas < vmax)
        & ~np.isclose(decadas, vmin, rtol=1e-12, atol=0)
    ]
    return np.concatenate(([vmin], decadas))


def plotar_contornos_logaritmicos(eixo, matrix, extent, vmin, vmax):
    """Desenha décadas e destaca o limiar configurado com uma linha mais espessa."""
    niveis = obter_niveis_contorno_logaritmicos(vmin, vmax)
    # Um nível só forma uma fronteira se o campo tiver valores dos dois lados.
    niveis = niveis[(niveis > np.min(matrix)) & (niveis < np.max(matrix))]
    if niveis.size == 0:
        return

    eixo.contour(
        matrix,
        levels=niveis,
        origin="lower",
        extent=extent,
        colors="white",
        linewidths=np.where(niveis == vmin, 1.2, 0.5),
    )


def criar_layout_mapa_com_barra(eixo_x, eixo_y, texto_resumo=None):
    """Cria mapa e barra horizontal, com espaço opcional para um resumo abaixo."""
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

    alturas = [altura_mapa, 0.35]
    altura_resumo = 0
    if texto_resumo:
        largura_texto = max(25, int(largura_figura * 12))
        linhas = [
            textwrap.fill(linha, width=largura_texto)
            for linha in texto_resumo.splitlines()
        ]
        texto_resumo = "\n".join(linhas)
        altura_resumo = 0.2 * len(texto_resumo.splitlines()) + 0.2
        alturas.append(altura_resumo)

    figura = plt.figure(
        figsize=(largura_figura, altura_mapa + 1.6 + altura_resumo),
        dpi=150,
        layout="constrained",
    )
    grade = figura.add_gridspec(
        len(alturas),
        1,
        height_ratios=alturas,
    )
    eixo_mapa = figura.add_subplot(grade[0])
    eixo_barra = figura.add_subplot(grade[1])
    if texto_resumo:
        eixo_resumo = figura.add_subplot(grade[2])
        eixo_resumo.set_axis_off()
        eixo_resumo.text(
            0, 0.5, texto_resumo,
            ha="left", va="center", fontsize=9,
            transform=eixo_resumo.transAxes,
        )
    return figura, eixo_mapa, eixo_barra


def plotar_heatmap_temporal(
    concentracoes_xy,
    eixo_x,
    eixo_y,
    evento,
    vmax_cores,
    cenario_id,
    max_concentracao_global,
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
    eixo.set_title(
        "C(x,y) ao nível do solo (z = 0 m)\n"
        f"Máximo global: {max_concentracao_global:.3e} {config.unidade}/m³"
    )
    eixo.set_xlabel("x (m)")
    eixo.set_ylabel("y (m)")
    eixo.axhline(y=0, linestyle="--", color="white", linewidth=0.5)
    eixo.axvline(x=0, linestyle="--", color="white", linewidth=0.5)

    if config.usar_escala_logaritmica and config.exibir_contornos_logaritmicos:
        plotar_contornos_logaritmicos(
            eixo,
            matrix,
            extent,
            config.vmin_logaritmico_efetivo,
            max_concentracao_global,
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
    resultado_superacao,
):
    """Salva um mapa XY de dose com a normalização configurada."""
    matrix = campo_dose_xy.transpose()
    max_dose_global = float(np.max(campo_dose_xy))
    extent = [eixo_x[0], eixo_x[-1], eixo_y[0], eixo_y[-1]]
    referencia = f"D ≥ {resultado_superacao.limiar_sv:.3e} Sv"
    if resultado_superacao.atingido:
        texto_resumo = (
            f"{referencia} | Área estimada: {resultado_superacao.area_m2 / 1e6:.4g} km²"
            f" | Alcance máximo: {resultado_superacao.alcance_maximo_m / 1000:.4g} km"
        )
    else:
        texto_resumo = f"{referencia}: limiar não atingido"
    figura, eixo, eixo_barra = criar_layout_mapa_com_barra(
        eixo_x, eixo_y, texto_resumo=texto_resumo,
    )
    imagem = eixo.imshow(
        matrix,
        origin="lower",
        extent=extent,
        aspect=1,
        norm=obter_normalizacao(vmax_cores, vmin_cores),
    )
    eixo.set_title(
        f"{titulo}\nMáximo global: {max_dose_global:.3e} Sv"
    )
    eixo.set_xlabel("x (m)")
    eixo.set_ylabel("y (m)")
    eixo.axhline(y=0, linestyle="--", color="white", linewidth=0.5)
    eixo.axvline(x=0, linestyle="--", color="white", linewidth=0.5)

    if config.usar_escala_logaritmica and config.exibir_contornos_logaritmicos:
        plotar_contornos_logaritmicos(
            eixo,
            matrix,
            extent,
            vmin_cores,
            max_dose_global,
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
            "usar escala logarítmica",vmax_cores
        )

    return LogNorm(vmin=vmin_logaritmico, vmax=vmax_cores)
