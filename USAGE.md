# Manual de Uso do PyTab

Guia prático para utilizar a ferramenta.

---

## 1. Executando

```bash
streamlit run pytab_app/streamlit_app.py
```

### Abra no navegador:

http://localhost:8501

## 2. Carregar Dados

O PyTab aceita:

    - CSV

    - Excel (.xlsx)

    - Arquivos com separadores inconsistentes

A tela inicial mostra:

    - prévia dos dados

    - tipos detectados

    - avisos sobre limpeza

    - tamanho do dataset

## 3. Fase MEDIR

### 3.1 Estatísticas

    - média

    - mediana

    - desvio padrão

    - coeficiente de variação

    - mínimo/máximo

### 3.2 Gráficos

    - série temporal agregada

    - média móvel

    - boxplot

    - outliers

### 3.3 Importante

    - agregação afeta APENAS visualização

    - outliers sempre usam dados brutos

## 4. Fase ANALISAR

### 4.1 Correlação

    - matriz completa

    - narrativa automática

### 4.2 Pareto

    - gráfico 80/20

    - linha cumulativa

### 4.3 Regressão Linear

    - interpretação automática

    - coeficientes

    - explicação simplificada

## 5. Dicas

    - sempre confiar na narrativa

    - sempre revisar outliers

    - sempre verificar data correta

6. Futuro da Ferramenta

    - testes estatísticos

    - relatórios PDF

    - gráficos de controle

    - regressão avançada