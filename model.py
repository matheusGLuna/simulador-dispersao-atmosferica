import numpy as np
from config import Config
from puff import Puff

class GaussianPuffModel:
    def __init__(self, config: Config):
        self.config = config

    def gerar_meshgrid_xyz(self, puff: Puff):

        x_max = self.config.dimensao_eixo_x
        x_step = self.config.passo_x
        y_max = self.config.dimensao_eixo_y
        y_step = self.config.passo_y
        z_max = self.config.dimensao_eixo_z
        z_step = self.config.passo_z

        num_x = int(x_max / x_step)
        num_y = int(2 * y_max / y_step) + 1
        num_z = int(z_max / z_step) + 1
        total_pontos = num_x * num_y * num_z

        if total_pontos > self.config.limite_pontos:
            error_string = (
                f"Essa modelagem resultaria em {total_pontos} pontos, acima do "
                f"limite parametrizado de {self.config.limite_pontos}.\n"
                "Aumente o limite parametrizado ou os intervalos (passos) entre pontos"
            )
            raise ValueError(error_string)

        x_vals = np.linspace(x_step, x_max, num_x)
        y_vals = np.linspace(-y_max, y_max, num_y)
        z_vals = np.linspace(0, z_max, num_z)

        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')

        return self.calcular_concentracao(X, Y, Z, puff), x_vals, y_vals, z_vals

    def calcular_concentracao(self, X, Y, Z, puff: Puff):
        
        idade_segundos = self.config.total_eventos - puff.instante_emissao
    
        x_centro = puff.velocidade_vento*idade_segundos
        
        sigma_y = self.calcular_sigma_y(x_centro, puff.classe_estabilidade)
        sigma_x = sigma_y
        sigma_z = self.calcular_sigma_z(x_centro, puff.classe_estabilidade)

        fator = (

            puff.atividade_emitida
            /
            (
                (2*np.pi)**1.5
                * sigma_x
                * sigma_y
                * sigma_z
            )
        )

        exp_x = np.exp(
            -((X - x_centro)**2)
            /(2*sigma_x**2)
        )

        exp_y = np.exp(
            -(Y**2)
            /(2*sigma_y**2)
        )

        exp_z1 = np.exp(
            -((Z-self.config.altura_chamine)**2)
            /(2*sigma_z**2)
        )

        exp_z2 = np.exp(
            -((Z+self.config.altura_chamine)**2)
            /(2*sigma_z**2)
        )

        return (
            fator
            * exp_x
            * exp_y
            * (exp_z1 + exp_z2)
        )

    def calcular_sigma_y(self, x, classe_estabilidade):
        classe = classe_estabilidade.upper()
        terreno = self.config.terreno.upper()

        if terreno == 'R':
            if classe == 'A':
                return 0.22 * x * (1 + 0.0001 * x) ** (-0.5)
            elif classe == 'B':
                return 0.16 * x * (1 + 0.0001 * x) ** (-0.5)
            elif classe == 'C':
                return 0.11 * x * (1 + 0.0001 * x) ** (-0.5)
            elif classe == 'D':
                return 0.08 * x * (1 + 0.0001 * x) ** (-0.5)
            elif classe == 'E':
                return 0.06 * x * (1 + 0.0001 * x) ** (-0.5)
            elif classe == 'F':
                return 0.04 * x * (1 + 0.0001 * x) ** (-0.5)
            else:
                raise ValueError("Classe de estabilidade inválida")

        elif terreno == 'U':
            if classe in ['A', 'B']:
                return 0.32 * x * (1 + 0.0004 * x) ** (-0.5)
            elif classe == 'C':
                return 0.22 * x * (1 + 0.0004 * x) ** (-0.5)
            elif classe == 'D':
                return 0.16 * x * (1 + 0.0004 * x) ** (-0.5)
            elif classe in ['E', 'F']:
                return 0.11 * x * (1 + 0.0004 * x) ** (-0.5)
            else:
                raise ValueError("Classe de estabilidade inválida")

        raise ValueError("Terreno inválido: use 'R' (rural) ou 'U' (urbano)")

    def calcular_sigma_z(self, x, classe_estabilidade):
        classe = classe_estabilidade.upper()
        terreno = self.config.terreno.upper()

        if terreno == 'R':
            if classe == 'A':
                return 0.20 * x
            elif classe == 'B':
                return 0.12 * x
            elif classe == 'C':
                return 0.08 * x * (1 + 0.0002 * x) ** (-0.5)
            elif classe == 'D':
                return 0.06 * x * (1 + 0.0015 * x) ** (-0.5)
            elif classe == 'E':
                return 0.03 * x * (1 + 0.0003 * x) ** (-1.0)
            elif classe == 'F':
                return 0.016 * x * (1 + 0.0003 * x) ** (-1.0)
            else:
                raise ValueError("Classe de estabilidade inválida")

        elif terreno == 'U':
            if classe in ['A', 'B']:
                return 0.24 * x * (1 + 0.001 * x) ** 0.5
            elif classe == 'C':
                return 0.20 * x
            elif classe == 'D':
                return 0.14 * x * (1 + 0.0003 * x) ** (-0.5)
            elif classe in ['E', 'F']:
                return 0.08 * x * (1 + 0.0015 * x) ** (-0.5)
            else:
                raise ValueError("Classe de estabilidade inválida")

        raise ValueError("Terreno inválido: use 'R' (rural) ou 'U' (urbano)")
