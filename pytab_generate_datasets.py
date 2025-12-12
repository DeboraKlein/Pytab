import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------
# Criar pasta de saída
# ---------------------------------------------------------
OUTPUT_DIR = "pytab_datasets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save(df, name):
    df.to_csv(os.path.join(OUTPUT_DIR, f"{name}.csv"), index=False)
    print(f"Gerado: {name}.csv")

# =========================================================
# 1) Dataset IMR (Individuais e Movimento da Média)
# =========================================================
np.random.seed(42)
imr_values = np.random.normal(loc=100, scale=5, size=200)
df_imr = pd.DataFrame({"Value": imr_values})
save(df_imr, "imr_dataset")

# =========================================================
# 2) Dataset Xbar-R (Subgrupos)
# =========================================================
subgroup_size = 5
n_groups = 40
data = np.random.normal(10, 2, size=subgroup_size * n_groups)

df_xr = pd.DataFrame({
    "Group": np.repeat(range(1, n_groups + 1), subgroup_size),
    "Value": data
})
save(df_xr, "xbar_r_dataset")

# =========================================================
# 3) Dataset P-Chart (Proporção de Defeituosos)
# =========================================================
n_samples = 50
sizes = np.random.randint(80, 150, n_samples)
defects = np.random.binomial(n=sizes, p=0.05)

df_p = pd.DataFrame({
    "Total": sizes,
    "Defectives": defects,
})
save(df_p, "p_chart_dataset")

# =========================================================
# 4) Dataset U-Chart (Defeitos por unidade)
# =========================================================
unit_counts = np.random.poisson(lam=2.5, size=60)
df_u = pd.DataFrame({"Defects": unit_counts})
save(df_u, "u_chart_dataset")

# =========================================================
# 5) Dataset para Teste t 1-amostra
# =========================================================
df_t1 = pd.DataFrame({"Value": np.random.normal(50, 10, 120)})
save(df_t1, "t_test_one_sample")

# =========================================================
# 6) Dataset para Teste t 2-amostras
# =========================================================
group_a = np.random.normal(60, 8, 80)
group_b = np.random.normal(65, 8, 75)

df_t2 = pd.DataFrame({
    "Value": np.concatenate([group_a, group_b]),
    "Group": ["A"] * len(group_a) + ["B"] * len(group_b)
})
save(df_t2, "t_test_two_samples")

# =========================================================
# 7) Dataset Teste Pareado
# =========================================================
before = np.random.normal(100, 10, 60)
after = before - np.random.normal(5, 3, 60)

df_paired = pd.DataFrame({"Before": before, "After": after})
save(df_paired, "t_test_paired")

# =========================================================
# 8) Dataset ANOVA
# =========================================================
g1 = np.random.normal(50, 5, 40)
g2 = np.random.normal(55, 5, 40)
g3 = np.random.normal(60, 5, 40)

df_anova = pd.DataFrame({
    "Value": np.concatenate([g1, g2, g3]),
    "Group": ["G1"] * len(g1) + ["G2"] * len(g2) + ["G3"] * len(g3)
})
save(df_anova, "anova_dataset")

# =========================================================
# 9) Dataset Qui-Quadrado
# =========================================================
table = pd.DataFrame({
    "Machine": np.repeat(["M1", "M2", "M3"], 40),
    "Defect": np.tile(np.random.choice(["Yes", "No"], 40), 3)
})
save(table, "chi_square_dataset")

# =========================================================
# 10) Dataset para Correlação
# =========================================================
x = np.random.normal(50, 10, 200)
y = 2 * x + np.random.normal(0, 8, 200)
z = np.random.normal(40, 5, 200)

df_corr = pd.DataFrame({"X": x, "Y": y, "Z": z})
save(df_corr, "correlation_dataset")

# =========================================================
# 11) Dataset para Regressão Linear
# =========================================================
x = np.linspace(0, 100, 200)
noise = np.random.normal(0, 10, 200)
y = 3 * x + 40 + noise

df_reg = pd.DataFrame({"X": x, "Y": y})
save(df_reg, "regression_dataset")

# =========================================================
# 12) Dataset para Normalidade
# =========================================================
normal = np.random.normal(100, 15, 300)
df_norm = pd.DataFrame({"Value": normal})
save(df_norm, "normality_dataset")

# =========================================================
# 13) Dataset com Outliers
# =========================================================
base = np.random.normal(100, 5, 180)
outliers = np.array([150, 160, 170, 180, 190])
df_out = pd.DataFrame({"Value": np.concatenate([base, outliers])})
save(df_out, "outliers_dataset")

# =========================================================
# 14) Dataset misto para testar várias fases
# =========================================================
df_mixed = pd.DataFrame({
    "Date": pd.date_range(start="2023-01-01", periods=200),
    "Revenue": np.random.normal(1000, 200, 200),
    "Profit": np.random.normal(200, 50, 200),
    "Category": np.random.choice(["A", "B", "C"], 200),
    "Defects": np.random.poisson(3, 200),
})
save(df_mixed, "mixed_dataset")

print("\n*** TODOS OS DATASETS FORAM GERADOS COM SUCESSO ***")
