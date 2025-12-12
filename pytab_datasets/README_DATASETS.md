# PyTab — Test Datasets Pack

Este diretório contém **14 datasets especialmente construídos** para validar:

- Estatísticas descritivas  
- Detecção de outliers  
- Séries temporais  
- Testes estatísticos (t, ANOVA, Qui-quadrado, normalidade)  
- Correlação  
- Regressão  
- Cartas de Controle (I-MR, Xbar–R, P e U)

Os datasets foram gerados artificialmente com distribuições controladas, permitindo
comparação direta entre:

- PyTab  
- Excel  
- Minitab  
- Python puro (pandas / scipy / statsmodels)

---

## Estrutura dos arquivos

Cada arquivo `.csv` representa um cenário de teste:

### **1. `imr_dataset.csv`**
Para validar:
- Carta I
- Carta MR
- Cálculo de médias móveis
- Estabilidade de processos individuais

---

### **2. `xbar_r_dataset.csv`**
Para validar:
- Carta Xbar–R
- Subgrupos
- Cálculo de R-bar e X-bar

---

### **3. `p_chart_dataset.csv`**
Para validar:
- Proporção de defeituosos
- Cartas P

---

### **4. `u_chart_dataset.csv`**
Para validar:
- Defeitos por unidade
- Cartas U

---

### **5. `t_test_one_sample.csv`**
Para validar:
- Teste t de 1 amostra
- Confiança, t-stat, p-value

---

### **6. `t_test_two_samples.csv`**
Para validar:
- Teste t de 2 amostras independentes

---

### **7. `t_test_paired.csv`**
Para validar:
- Teste t pareado

---

### **8. `anova_dataset.csv`**
Para validar:
- ANOVA One-Way
- Comparação entre 3 grupos

---

### **9. `chi_square_dataset.csv`**
Para validar:
- Teste de independência qui-quadrado (tabela de contingência)

---

### **10. `correlation_dataset.csv`**
Para validar:
- Correlações altas e moderadas
- Matriz de calor (Heatmap)

---

### **11. `regression_dataset.csv`**
Para validar:
- Regressão linear simples
- R² conhecido (próximo de 0.95)

---

### **12. `normality_dataset.csv`**
Para validar:
- Shapiro–Wilk  
- QQ-Plot

---

### **13. `outliers_dataset.csv`**
Para validar:
- Z-score  
- IQR  
- MAD  
- Outlier automático  
- Visualização boxplot

---

### **14. `mixed_dataset.csv`**
Para validar:
- Todas as fases do PyTab
- Ideal para revisar fluxo completo DMAIC

---

### Como usar

1. Abra o PyTab  
2. Carregue cada dataset  
3. Compare outputs entre PyTab, Excel e Minitab  
4. Registre diferenças (se houver)  

---

# Garantia de qualidade

Todos os datasets têm sementes fixas (`np.random.seed(42)`), garantindo resultados reprodutíveis.

