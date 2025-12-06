# Arquitetura do PyTab

O PyTab é organizado em camadas, para separar responsabilidades e facilitar a evolução do projeto.

## Módulos principais

### 1. pytab.io.reader

Responsável por:

- Leitura de arquivos CSV e Excel.
- Tentativas com diferentes separadores e encodings.
- Tratamento de casos comuns de arquivos gerados por Excel.

### 2. pytab.stats.descriptive

Responsável por:

- Cálculo de estatísticas descritivas:
  - média, mediana, desvio-padrão, mínimo, máximo, quartis.
- Interface simples para sumarizar colunas numéricas.

### 3. pytab.charts.control_chart

Responsável por:

- Cálculo de métricas necessárias a gráficos de controle.
- Construção de dados que podem ser usados em plotly ou matplotlib.

### 4. pytab.reports.pdf_report

Responsável por:

- Composição de relatórios técnicos e executivos.
- Inserção de gráficos e tabelas.
- Exportação em formato PDF.

### 5. pytab_app.streamlit_app

Responsável por:

- Interface interativa em navegador.
- Upload de arquivos.
- Escolha de colunas.
- Apresentação de estatísticas e gráficos.

