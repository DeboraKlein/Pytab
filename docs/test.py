import pandas as pd
import numpy as np
import os

# Create output directory
out_dir = "/mnt/data/pytab_datasets"
os.makedirs(out_dir, exist_ok=True)

datasets = {}

# 1. IMR dataset (individual measurements)
np.random.seed(42)
imr = pd.DataFrame({
    "Date": pd.date_range("2024-01-01", periods=120, freq="D"),
    "Value": np.random.normal(loc=50, scale=5, size=120)
})
datasets["imr"] = imr

# 2. Xbar-R dataset (subgroups)
xbar = pd.DataFrame({
    "Subgroup": np.repeat(np.arange(1, 31), 5),
    "Measurement": np.random.normal(loc=10, scale=1, size=150)
})
datasets["xbar_r"] = xbar

# 3. P-Chart dataset
p_chart = pd.DataFrame({
    "Sample": np.arange(1, 51),
    "Defectives": np.random.binomial(100, 0.07, 50),
    "SampleSize": np.repeat(100, 50)
})
datasets["p_chart"] = p_chart

# 4. U-Chart dataset
u_chart = pd.DataFrame({
    "Sample": np.arange(1, 51),
    "Defects": np.random.poisson(4, 50),
    "Units": np.repeat(1, 50)
})
datasets["u_chart"] = u_chart

# 5. ANOVA dataset
anova = pd.DataFrame({
    "Group": np.repeat(["A", "B", "C"], 40)
})
anova["Value"] = np.concatenate([
    np.random.normal(50, 5, 40),
    np.random.normal(52, 5, 40),
    np.random.normal(48, 5, 40)
])
datasets["anova"] = anova

# 6. Teste t 1 amostra
t1 = pd.DataFrame({
    "Measure": np.random.normal(100, 15, 200)
})
datasets["t1_sample"] = t1

# 7. Teste t 2 amostras
t2 = pd.DataFrame({
    "Group": np.repeat(["Control", "Treatment"], 100)
})
t2["Value"] = np.concatenate([
    np.random.normal(70, 10, 100),
    np.random.normal(75, 10, 100)
])
datasets["t2_sample"] = t2

# 8. Teste pareado
paired = pd.DataFrame({
    "Before": np.random.normal(80, 8, 60),
    "After": np.random.normal(78, 8, 60)
})
datasets["paired"] = paired

# 9. Regressão simples
adv = np.random.uniform(0, 100, 200)
sales = pd.DataFrame({"Advertising": adv})
sales["Sales"] = 20 + 0.7 * sales["Advertising"] + np.random.normal(0, 5, 200)
datasets["regressao_simples"] = sales

# 10. Regressão múltipla
temp = np.random.uniform(15, 35, 200)
press = np.random.uniform(1, 10, 200)
multi = pd.DataFrame({
    "Temp": temp,
    "Pressure": press
})
multi["Output"] = 5 + 2 * multi["Temp"] - 1.5 * multi["Pressure"] + np.random.normal(0, 3, 200)
datasets["regressao_multipla"] = multi

# 11. Correlação
X = np.random.normal(0, 1, 300)
corr = pd.DataFrame({"X": X})
corr["Y"] = 0.4 * corr["X"] + np.random.normal(0, 1, 300)
corr["Z"] = np.random.normal(0, 1, 300)
datasets["correlacao"] = corr

# 12. Outliers (Z-score/IQR)
out = pd.DataFrame({
    "Value": np.concatenate([
        np.random.normal(100, 10, 200),
        [200, 220, 250, 10, 5]
    ])
})
datasets["outliers"] = out

# 13. Time series with trend + outliers
trend = np.linspace(50, 100, 200)
ts = pd.DataFrame({
    "Date": pd.date_range("2023-01-01", periods=200, freq="D"),
    "Value": trend + np.random.normal(0, 3, 200)
})
ts.loc[50, "Value"] = 150
ts.loc[150, "Value"] = 10
datasets["timeseries_outliers"] = ts

# 14. Qui-quadrado
chi = pd.DataFrame({
    "Machine": np.random.choice(["M1", "M2", "M3"], 300),
    "Defect": np.random.choice(["Yes", "No"], 300, p=[0.2, 0.8])
})
datasets["quiquadrado"] = chi

# SAVE CSVs
file_links = {}
for name, df in datasets.items():
    path = f"{out_dir}/{name}.csv"
    df.to_csv(path, index=False)
    file_links[name] = path

file_links
