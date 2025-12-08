<p align="center">
  <img src=docs/assets/Pytab_logo_H.svg alt="PyTab Logo" width="400">
</p>


# PyTab – Roadmap

Este documento descreve as principais etapas de evolução do PyTab.

## Versão 0.1.0 – Fundamentos

- [ ] Leitura robusta de CSV e Excel (incluindo separadores problemáticos).
- [ ] Detecção automática de tipos de coluna:
  - Numéricas
  - Categóricas
  - Datas
- [ ] Estatísticas descritivas básicas:
  - média, mediana, desvio-padrão, mínimos, máximos, quartis.
- [ ] Estrutura base para gráficos:
  - histograma
  - boxplot
  - distribuição (curva aproximada)
- [ ] Esqueleto do app Streamlit:
  - upload de arquivo
  - seleção de coluna
  - visualização básica.

## Versão 0.2.0 – Distribuição e Outliers

- [ ] Cálculo automático de z-score por coluna numérica.
- [ ] Identificação de outliers.
- [ ] Visualizações:
  - histograma com destaque de outliers.
  - boxplot com realce de pontos extremos.
- [ ] Tabela de outliers por coluna.

## Versão 0.3.0 – Gráficos de Controle (SPC)

- [ ] Gráfico de controle simples (XmR).
- [ ] Cálculo de limites de controle.
- [ ] Suporte a séries temporais com coluna de data.
- [ ] Interface no app para escolher coluna e granularidade.

## Versão 0.4.0 – Pareto e Estratificação

- [ ] Geração de gráfico de Pareto para colunas categóricas.
- [ ] Filtros combinando numéricas, categorias e datas.
- [ ] Drill-down: seleção de subgrupos para análise focada.

## Versão 0.5.0 – Relatórios em PDF

- [ ] Geração automática de relatório em PDF contendo:
  - estatísticas descritivas,
  - gráficos principais,
  - tabela de outliers,
  - seção de observações.
- [ ] Inclusão de resumo executivo (texto geral) e resumo técnico.

## Versão 1.0.0 – Lançamento Oficial

- [ ] Publicação oficial no PyPI.
- [ ] Documentação completa em `docs/`.
- [ ] Testes automatizados cobrindo os módulos principais.
- [ ] Exemplos práticos em notebooks (ex: qualidade, finanças, saúde).
