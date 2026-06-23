Projeto

Simulador computacional para Trabalho de Graduação (TG) do curso de Engenharia de Energia da UFABC.

Título provisório:

"Modelagem Computacional da Dispersão Atmosférica de Radionuclídeos Utilizando as Equações de Pasquill-Gifford em Cenários Dinâmicos de Segurança Nuclear"

Objetivo científico:

Desenvolver um modelo computacional para simulação da dispersão atmosférica de radionuclídeos em cenários hipotéticos de acidentes nucleares. O modelo é baseado nas equações gaussianas de Pasquill-Gifford e nas parametrizações de Briggs para ambientes rurais e urbanos. O objetivo é evoluir um modelo originalmente estacionário para um modelo temporal capaz de representar cenários atmosféricos não estacionários.

Tecnologias:

Python
Git/GitHub
VS Code

Estrutura atual aproximada:

src/
├── config.py
├── model.py
├── temporal_model.py
├── plotting.py
├── main.py

Responsabilidades dos módulos:

config.py

Define todos os parâmetros de simulação.
Utiliza dataclasses.
Deve centralizar configurações físicas e numéricas.

model.py

Implementa o modelo gaussiano de Pasquill-Gifford.
Responsável exclusivamente pelos cálculos físicos.
Não deve gerar gráficos.

temporal_model.py

Responsável pela evolução temporal do cenário.
Gerencia eventos discretos de emissão.
Define séries temporais para vento, emissão e estabilidade atmosférica.

plotting.py

Responsável apenas pela visualização.
Não deve conter lógica física.

main.py

Orquestra a execução completa da simulação.
Estado atual do modelo

O modelo atual:

Gera um campo tridimensional de concentração.
Utiliza meshgrids 3D (x, y, z).
Produz mapas 2D (cortes 2D) XY, XZ e YZ.
Considera vento inicialmente orientado na direção positiva do eixo x.
Implementa classes de estabilidade atmosférica A-F.

Evolução de estacionario para temporal adotada:

O modelo temporal será baseado em eventos discretos de intervalo definido (em geral, de 1h)

Exemplo:

duração total do acidente = 24 horas
intervalo entre eventos = 1 hora
total de eventos = 24

Cada evento possui:

velocidade do vento própria;
classe de estabilidade própria.

Essas variáveis podem variar temporalmente.
Inicialmente a direção do vento permanecerá fixa no sentido do eixo X positivo

Abordagem física escolhida:

Foi adotada uma abordagem baseada em superposição.

Para cada evento temporal:

Calcula-se um campo de concentração independente.
O campo total do cenário é obtido pela soma dos campos de todos os eventos anteriores.
A abordagem representa uma sequência de liberações discretas (jatos puff simplificados).

Futuras expansões previstas:

direção do vento variável;
cálculo de doses radiológicas;
análise estatística com aplicação de IA;

Regras importantes de desenvolvimento:

Priorizar legibilidade e modularização.
Evitar duplicação de código.
Sempre preferir soluções orientadas a objetos quando aumentarem a clareza.
Manter tipagem explícita quando possível.
Utilizar nomes de variáveis em português técnico ou inglês técnico de forma consistente.
Priorizar funções pequenas e coesas.

Ao propor modificações:

preservar compatibilidade sempre que possível;
justificar alterações arquiteturais;
explicar impactos físicos das mudanças;

Grandezas importantes:

atividade liberada [Ci ou Bq]
taxa de emissão [Ci/h ou Bq/h]
concentração atmosférica [Bq/m³ ou Ci/m³]
velocidade do vento [m/s]
altura efetiva da pluma [m]
coeficientes sigma_y e sigma_z [m]