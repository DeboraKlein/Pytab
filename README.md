<p align="center">
  <img src="Pytab_logo_H.svg" alt="PyTab logo" width="360">
</p>



<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg" alt="License: MIT">
  </a>
  <img src="https://img.shields.io/badge/status-alpha-blue.svg" alt="Status: Alpha">
  <img src="https://img.shields.io/badge/built_with-Streamlit-red.svg" alt="Built with Streamlit">
</p>

# PyTab

Análises estatísticas rápidas, acessíveis e open-source.

---

## Visão Geral

**PyTab** é um toolkit estatístico inspirado no Minitab, projetado para oferecer análises confiáveis e acessíveis para profissionais de **dados**, **qualidade**, **Lean Six Sigma** e **gestão de processos**.

O foco é entregar:

- leitura robusta de dados reais (inclusive CSVs problemáticos)
- métodos estatísticos fundamentais
- ferramentas de análise exploratória
- integração natural com Python e Streamlit
- geração futura de relatórios automáticos (PDF)

O PyTab nasce como alternativa aberta e extensível a ferramentas proprietárias.

---

## Para quem é o PyTab?

O PyTab é voltado para profissionais que precisam de análises rápidas, práticas e auditáveis:

- Analistas de Dados  
- Cientistas de Dados  
- Engenheiros de Qualidade  
- Green Belts / Black Belts  
- Gestores de Processos  
- Pesquisadores  
- Estudantes  

---

## Lean Six Sigma (LSS) + Estatística

PyTab implementa gradualmente os métodos mais usados em LSS:

- Estatística descritiva  
- Estimativa de variabilidade  
- Z-score e detecção de outliers  
- Histogramas e boxplots  
- Gráficos de controle (SPC)  
- Análises exploratórias de causa  

O objetivo é permitir que times pratiquem DMAIC com ferramentas modernas e open-source.

---

## Funcionalidades Atuais (v0.1.0)

###  Leitura robusta de dados  
- Tolerante a separadores inconsistentes  
- Tolerante a encodings diferentes  
- Detecção automática de formato  
- Suporte a CSV e, em breve, Excel  

###  Estatísticas descritivas  
- Média, mediana, mínimo, máximo  
- Desvio padrão  
- Contagem e valores faltantes  
- Tabela padronizada para DataFrames  

###  Aplicativo Streamlit  
- Upload de arquivos  
- Visualização de prévia  
- Estatísticas básicas instantâneas  

###  Estrutura modular da biblioteca  
- `io/` — carregamento de dados  
- `stats/` — funções estatísticas  
- `charts/` — geração de gráficos  
- `reports/` — exportação e relatórios  
- `utils/` — funções auxiliares  

---

## Roadmap

Veja o planejamento completo em:  
[`ROADMAP.md`](ROADMAP.md)

Próximas entregas incluem:

- Z-score e outliers avançados  
- Histogramas automáticos  
- Gráficos de controle (XmR)  
- Relatórios PDF automáticos  
- Interface Streamlit completa  
- Publicação no PyPI  

---

## Arquitetura do Projeto



O projeto segue um modelo modular, separando claramente responsabilidades:

````
Pytab/
├─ pytab/
│  ├─ __init__.py
│  ├─ io/
│  │  └─ reader.py
│  ├─ stats/
│  │  ├─ descriptive.py
│  │  └─ outliers.py
│  ├─ utils/
│  │  └─ schema.py
│  └─ charts/
│     └─ theme.py          
│
├─ pytab_app/
│  ├─ __init__.py          
│  ├─ utils.py             
│  ├─ fases/
│  │  ├─ __init__.py       
│  │  ├─ medir.py          
│  │  ├─ analisar.py       
│  │  ├─ melhorar.py      
│  │  └─ controlar.py      
│  └─ streamlit_app.py     
│
├── docs/
│   ├── architecture.md
│   ├── dmaic_overview.md
│   ├── modules.md
│   └── usage.md
│
├── tests/
│   └── test_reader.py
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── README.md
├── ROADMAP.md
├── LICENSE.md
├── pyproject.toml
└── .gitignore

````


Documentação técnica detalhada está em `docs/`.

---

## 6. Instalação e uso

### Clonar o repositório
```bash
git clone https://github.com/DeboraKlein/Pytab
cd PyTab
```


### Instalação em modo desenvolvimento:
```bash
pip install -e .
```

### Executar o aplicativo:
```bash
streamlit run pytab_app/streamlit_app.py
```

---

## 7. Contribuição

Contribuições são bem-vindas.

- Leia `docs/architecture.md` para entender a estrutura interna  
- Consulte `ROADMAP.md` para ver o planejamento  
- Use os templates de issues para reportar problemas ou sugerir funcionalidades

---

## 8. Licença

PyTab é distribuído sob a licença MIT License, permitindo uso, modificação e distribuição livre.

Consulte o arquivo `LICENSE.md`
 para detalhes.



