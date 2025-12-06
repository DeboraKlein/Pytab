# Módulos do PyTab

Documentação técnica detalhada dos módulos da biblioteca `pytab/`.

---

## pytab.io
### reader.py
- `read_csv_smart(path)`
- `read_excel_smart(path)`
- `read_any(path)`

Funções responsáveis por leitura robusta de dados.

---

## pytab.stats
### descriptive.py
- `summarize_numeric(df)`

Estatísticas descritivas.

---

## pytab.charts
### control_chart.py
- `calculate_basic_control_limits(series)`

Base para gráficos de controle.

---

## pytab.reports
### pdf_report.py
- `create_simple_report(path, title)`

Base para geração de relatórios PDF.

---

## pytab.utils
### schema.py
- `detect_column_types(df)`

Detecção automática de colunas numéricas, categóricas e datas.
