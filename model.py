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

        num_x = int(2 * x_max / x_step)
        num_y = int(2 * y_max / y_step)
        num_z = int(z_max / z_step)
        total_pontos = num_x * num_y * num_z

        if total_pontos > self.config.limite_pontos:
            error_string = (
                f"Essa modelagem resultaria em {total_pontos} pontos, acima do "
                f"limite parametrizado de {self.config.limite_pontos}.\n"
                "Aumente o limite parametrizado ou os intervalos (passos) entre pontos"
            )
            raise ValueError(error_string)

        x_vals = np.linspace(-x_max, x_max, num_x)
        y_vals = np.linspace(-y_max, y_max, num_y)
        z_vals = np.linspace(1, z_max, num_z)

        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')

        return self.calcular_concentracao(X, Y, Z, puff), x_vals, y_vals, z_vals

    def calcular_concentracao(self, X, Y, Z, puff: Puff):
        
        angulo_graus = puff.angulo_vento % 360
        angulo_rad = np.deg2rad(angulo_graus)

        centro_x = puff.idade*puff.velocidade_vento*np.cos(angulo_rad)
        centro_y = puff.idade*puff.velocidade_vento*np.sin(angulo_rad)

        sigma_y = self.calcular_sigma_y(puff)
        sigma_z = self.calcular_sigma_z(puff)
        sigma_x = sigma_y

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
            -((X - centro_x)**2)
            /(2*sigma_x**2)
        )

        exp_y = np.exp(
            -((Y - centro_y)**2)
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

        concentracao = fator*exp_x* exp_y*(exp_z1 + exp_z2)
        
        return concentracao

    def calcular_sigma_y(self, puff: Puff):
        classe = puff.classe_estabilidade.upper()
        terreno = self.config.terreno.upper()
        coeficientes = self.obter_coeficientes_sigma(terreno, classe)

        a = coeficientes['a']
        b = coeficientes['b']

        distancia_centro_puff = puff.velocidade_vento*puff.idade
        return a * distancia_centro_puff ** b

    def calcular_sigma_z(self, puff: Puff):
        classe = puff.classe_estabilidade.upper()
        terreno = self.config.terreno.upper()
        coeficientes = self.obter_coeficientes_sigma(terreno, classe)

        c = coeficientes['c']
        d = coeficientes['d']

        distancia_centro_puff = puff.velocidade_vento*puff.idade
        return c * distancia_centro_puff ** d

    def obter_coeficientes_sigma(self, terreno, classe):
        coeficientes = {
            'R': {
                'A': {'a': 0.18, 'b': 0.92, 'c': 0.72, 'd': 0.80},
                'B': {'a': 0.14, 'b': 0.92, 'c': 0.53, 'd': 0.80},
                'C': {'a': 0.10, 'b': 0.92, 'c': 0.34, 'd': 0.80},
                'D': {'a': 0.06, 'b': 0.92, 'c': 0.15, 'd': 0.80},
                'E': {'a': 0.045, 'b': 0.92, 'c': 0.12, 'd': 0.80},
                'F': {'a': 0.03, 'b': 0.92, 'c': 0.08, 'd': 0.80},
            },
            'U': {
                'A': {'a': 0.32, 'b': 0.90, 'c': 0.24, 'd': 0.91},
                'B': {'a': 0.32, 'b': 0.90, 'c': 0.24, 'd': 0.91},
                'C': {'a': 0.22, 'b': 0.90, 'c': 0.14, 'd': 0.91},
                'D': {'a': 0.16, 'b': 0.90, 'c': 0.08, 'd': 0.91},
                'E': {'a': 0.11, 'b': 0.90, 'c': 0.04, 'd': 0.91},
                'F': {'a': 0.11, 'b': 0.90, 'c': 0.04, 'd': 0.91},
            },
        }

        if terreno not in coeficientes:
            raise ValueError("Terreno inválido: use 'R' (rural) ou 'U' (urbano)")

        if classe not in coeficientes[terreno]:
            raise ValueError("Classe de estabilidade inválida")

        return coeficientes[terreno][classe]
