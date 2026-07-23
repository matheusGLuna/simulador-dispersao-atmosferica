from dataclasses import dataclass

@dataclass
class Config:

    arquivo_cenario: str = "dados_cenarios/IEN_TARDE_ENSOLARADA_001_EXPANDIDA.json"

    converter_ci_bq: bool = True   # True para converter atividades de entrada em Ci para Bq, False para manter em Ci
    FATOR_CI_PARA_BQ = 3.7e10

    altura_chamine: int = 10        # [m]
    terreno: str = "R"              # R para rural, U para urbano

    dim_eixo_x_pos: int = 0         # [m] inteiro >= 1 e multiplo de passo_x
    dim_eixo_x_neg: int = 30000     # [m] inteiro >= 0 e multiplo de passo_x
    dim_eixo_y_pos: int = 30000     # [m] inteiro >= 1 e multiplo de passo_y
    dim_eixo_y_neg: int = 0         # [m] inteiro >= 0 e multiplo de passo_y
    passo_x: int = 50               # [m] inteiro >= 1
    passo_y: int = 50               # [m] inteiro >= 1
    limite_pontos: int = 1002001    # limite de pontos por malha calculada

    simular_apenas_estado_final: bool = False
    simular_evolucao_temporal_estados: bool = True
    gerar_plotagens_temporais: bool = True
    gerar_video_temporal: bool = False

    gamma: float = 0.3              # 0.3 a 0.6; usado apenas na escala convencional
    usar_escala_logaritmica: bool = True
    vmin_logaritmico: float = 2.702e-11
    vmax_animacao: float | None = None  # [Ci/m³]; None usa o máximo global calculado
    exibir_contornos_logaritmicos: bool = True
    quantidade_contornos_logaritmicos: int = 8
    
    diretorio_dados_parciais: str = "dados_parciais"
    diretorio_plotagens_parciais: str = "plotagens_parciais"
    diretorio_dados_acumulados: str = "dados_acumulados"
    diretorio_plotagens_acumuladas: str = "plotagens_acumuladas"

    @property
    def unidade(self):
        """Unidade de atividade definida pela configuração de conversão."""
        return "Bq" if self.converter_ci_bq else "Ci"

    @property
    def fator_conversao_atividade(self):
        """Fator para converter atividades de entrada em Ci à unidade ativa."""
        return self.FATOR_CI_PARA_BQ if self.converter_ci_bq else 1.0

    @property
    def vmin_logaritmico_efetivo(self):
        """Limiar logarítmico expresso na unidade ativa da simulação."""
        return self.vmin_logaritmico * self.fator_conversao_atividade

    @property
    def vmax_animacao_efetivo(self):
        """Teto de cores da animação expresso na unidade ativa da simulação."""
        if self.vmax_animacao is None:
            return None
        return self.vmax_animacao * self.fator_conversao_atividade
