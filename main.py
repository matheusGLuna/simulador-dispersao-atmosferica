import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

from config import Config
from model import GaussianPlumeModel

class AtmosphericDispersionSimulator:
    def __init__(self, config: Config):
        self.config = config
        self.model = GaussianPlumeModel(config)
        self.concentracoes_xyz = None
        self.eixo_x = None
        self.eixo_y = None
        self.eixo_z = None

    def run(self):
        if self.config.calcular_ponto_especifico:
            self._calcular_ponto_especifico()

        if self.config.gerar_meshgrid_xyz:
            self._gerar_meshgrid_xyz()

        if self.config.plotar_heatmap_xy:
            self._plot_heatmap_xy()

        if self.config.plotar_heatmap_yz:
            self._plot_heatmap_yz()

        if self.config.plotar_heatmap_xz:
            self._plot_heatmap_xz()

        plt.show()

    def _calcular_ponto_especifico(self):
        # ============================================================================
        # Calcula concentração C(x=a,y=b,z=c) apenas no ponto particular informado
        # ============================================================================
        x_particular = abs(self.config.x_calculo)
        y_particular = abs(self.config.y_calculo)
        z_particular = abs(self.config.z_calculo)

        concentracao = self.model.calcular_concentracao(
            x_particular,
            y_particular,
            z_particular,
        )

        print(
            f"No ponto solicitado: C({x_particular},{y_particular},{z_particular}) = "
            f"{concentracao:.3e} {self.config.unidade}/m³\n"
        )

    def _gerar_meshgrid_xyz(self):
        # ============================================================================
        # Gera meshgrid 3d de concentrações C(x,y,z) para todos os pontos no espaço
        # ============================================================================
        self.concentracoes_xyz, self.eixo_x, self.eixo_y, self.eixo_z = (
            self.model.gerar_meshgrid_xyz()
        )
        print("meshgrid de concentrações C(x,y,z) modelado com sucesso\n")

    def _plot_heatmap_xy(self):
        # =============================================================================
        # Plota um heatmap 2D a uma altura Z de corte desejada
        # =============================================================================
        self._check_meshgrid_generated()

        z_corte = self.config.z_corte
        z_step = self.config.passo_z
        z_max = self.config.dimensao_eixo_z

        if not (0 <= z_corte <= z_max):
            raise ValueError(
                "z_corte deve estar no domínio (>= 0 e <= dimensao_eixo_z)"
            )

        if z_corte % z_step != 0:
            raise ValueError(
                "z_corte deve ser múltiplo inteiro de passo_z (ou zero)"
            )

        i_z_corte = int(z_corte // z_step)
        malha_xy = self.concentracoes_xyz[:, :, i_z_corte]

        x_i, y_i = np.unravel_index(np.argmax(malha_xy), malha_xy.shape)
        x_max = self.eixo_x[x_i]
        y_max = self.eixo_y[y_i]

        print(
            f"C(x,y,z={z_corte}) máximo no corte é de {malha_xy[x_i, y_i]:.3e} "
            f"{self.config.unidade}/m³"
        )
        print(f"Ocorre em x = {x_max:.2f} m e y= {y_max:.2f}m\n")

        malha_yx = malha_xy.transpose()
        # Transpondo para representação mais adequada na plotagem do inshow

        self._render_heatmap(
            matrix=malha_yx,
            extent=[
                self.config.passo_x,
                self.config.dimensao_eixo_x,
                -self.config.dimensao_eixo_y,
                self.config.dimensao_eixo_y,
            ],
            title=f"C(x,y) no plano z =  {z_corte} m",
            xlabel="x (m)",
            ylabel="y (m)",
            filename=f"heatmap_xy_z{z_corte}.png",
            hlines=[(0, '--', 'white')],
        )

    def _plot_heatmap_yz(self):
        # =============================================================================
        # Plota um heatmap 2D a uma distancia y de corte desejada
        # =============================================================================
        self._check_meshgrid_generated()

        x_corte = self.config.x_corte
        x_step = self.config.passo_x
        x_max = self.config.dimensao_eixo_x

        if not (x_step <= x_corte <= x_max):
            raise ValueError(
                "x_corte deve estar no domínio (>= passo_x e <= dimensao_eixo_x)"
            )

        if x_corte % x_step != 0:
            raise ValueError("x_corte deve ser múltiplo inteiro de passo_x")

        i_x_corte = int((x_corte - x_step) // x_step)
        malha_yz = self.concentracoes_xyz[i_x_corte, :, :]

        y_i, z_i = np.unravel_index(np.argmax(malha_yz), malha_yz.shape)
        y_max = self.eixo_y[y_i]
        z_max = self.eixo_z[z_i]

        print(
            f"C(y,z,x={x_corte}) máximo no corte é de {malha_yz[y_i, z_i]:.3e} "
            f"{self.config.unidade}/m³"
        )
        print(f"Ocorre em y = {y_max:.2f} m e z= {z_max:.2f}m\n")

        malha_zy = malha_yz.transpose()
        # Transpondo para representação mais adequada na plotagem do inshow

        self._render_heatmap(
            matrix=malha_zy,
            extent=[
                -self.config.dimensao_eixo_y,
                self.config.dimensao_eixo_y,
                0,
                self.config.dimensao_eixo_z,
            ],
            title=f"C(y,z) no plano x = {x_corte} m",
            xlabel="y (m)",
            ylabel="z (m)",
            filename=f"heatmap_yz_x{x_corte}.png",
            hlines=[(self.config.altura_chamine, '--', 'white')],
            vlines=[(0, '--', 'white')],
        )

    def _plot_heatmap_xz(self):
        # =============================================================================
        # Plota um heatmap 2D a uma distancia y de corte desejada
        # =============================================================================
        self._check_meshgrid_generated()

        y_corte = self.config.y_corte
        y_step = self.config.passo_y
        y_max = self.config.dimensao_eixo_y

        if not (-y_max <= y_corte <= y_max):
            raise ValueError(
                "y_corte deve satisfazer: -dimensao_eixo_y <= y_corte <= dimensao_eixo_y"
            )

        if y_corte % y_step != 0:
            raise ValueError("y_corte deve ser múltiplo inteiro de passo_y (ou zero)")

        i_y_corte = int((y_corte + y_max) // y_step)
        malha_xz = self.concentracoes_xyz[:, i_y_corte, :]

        x_i, z_i = np.unravel_index(np.argmax(malha_xz), malha_xz.shape)
        x_max = self.eixo_x[x_i]
        z_max = self.eixo_z[z_i]

        print(
            f"C(x,z,y={y_corte}) máximo no corte é de {malha_xz[x_i, z_i]:.3e} "
            f"{self.config.unidade}/m³"
        )
        print(f"Ocorre em x = {x_max:.2f} m e z= {z_max:.2f}m\n")

        malha_zx = malha_xz.transpose()
        # Transpondo para representação mais adequada na plotagem do inshow

        self._render_heatmap(
            matrix=malha_zx,
            extent=[
                self.config.passo_x,
                self.config.dimensao_eixo_x,
                0,
                self.config.dimensao_eixo_z,
            ],
            title=f"C(x,z) no plano y = {y_corte} m",
            xlabel="x (m)",
            ylabel="z (m)",
            filename=f"heatmap_xz_y{y_corte}.png",
            aspect=4,
            hlines=[(self.config.altura_chamine, '--', 'white')],
        )

    def _render_heatmap(
        self,
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
            norm=PowerNorm(self.config.gamma),
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
        cbar.set_label(f"Concentração em {self.config.unidade}/m³")

        try:
            plt.tight_layout()
            plt.savefig(filename, dpi=150)
        except Exception as e:
            print(f"Falha ao salvar {filename}: {e}")

    def _check_meshgrid_generated(self):
        if self.concentracoes_xyz is None:
            raise ValueError("heatmap 2D tem como pré req a criação do meshgrid 3D")


if __name__ == "__main__":
    config = Config()
    simulator = AtmosphericDispersionSimulator(config)
    simulator.run()
