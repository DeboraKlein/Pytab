"""
pytab.core.analysis_specs
-------------------------
Especificações declarativas dos requisitos estatísticos
para cada tipo de análise suportada pelo PyTab.

Este módulo NÃO executa cálculos.
Ele define contratos (roles, constraints e defaults)
para serem usados por:
- variable_resolver
- UI (Streamlit)
- validação
"""

from typing import Dict, Any, List


ANALYSIS_SPECS: Dict[str, Dict[str, Any]] = {

    # ======================================================
    # TESTES t
    # ======================================================

    "t_test_one_sample": {
        "label": "Teste t — 1 amostra",
        "requires": {
            "numeric": {
                "count": 1,
                "constraints": ["numeric"]
            }
        },
        "parameters": {
            "mu0": {
                "type": "float",
                "default": "mean"
            }
        },
        "min_n": 3,
        "description": "Compara a média de uma variável numérica com um valor hipotético."
    },

    "t_test_two_samples": {
        "label": "Teste t — 2 amostras independentes",
        "requires": {
            "numeric": {
                "count": 1,
                "constraints": ["numeric"]
            },
            "group": {
                "count": 1,
                "constraints": [
                    "categorical",
                    "n_unique>=2"
                ]
            }
        },
        "group_rules": {
            "prefer_exact_n_groups": 2,
            "max_groups": 10
        },
        "min_n_per_group": 2,
        "description": "Compara médias entre dois grupos independentes."
    },

    "t_test_paired": {
        "label": "Teste t — pareado",
        "requires": {
            "numeric_pair": {
                "count": 2,
                "constraints": [
                    "numeric",
                    "paired"
                ]
            }
        },
        "min_n_pairs": 3,
        "description": "Compara médias de duas medições pareadas (antes/depois)."
    },

    # ======================================================
    # ANOVA
    # ======================================================

    "anova_oneway": {
        "label": "ANOVA One-Way",
        "requires": {
            "numeric": {
                "count": 1,
                "constraints": ["numeric"]
            },
            "factor": {
                "count": 1,
                "constraints": [
                    "categorical",
                    "n_unique>=3",
                    "n_unique<=20"
                ]
            }
        },
        "min_n_per_group": 3,
        "description": "Testa diferença de médias entre três ou mais grupos."
    },

    # ======================================================
    # QUI-QUADRADO
    # ======================================================

    "chi_square_independence": {
        "label": "Qui-Quadrado de Independência",
        "requires": {
            "row_var": {
                "count": 1,
                "constraints": [
                    "categorical",
                    "n_unique>=2"
                ]
            },
            "col_var": {
                "count": 1,
                "constraints": [
                    "categorical",
                    "n_unique>=2"
                ]
            }
        },
        "min_total_n": 10,
        "description": "Avalia associação entre duas variáveis categóricas."
    },

    # ======================================================
    # NORMALIDADE
    # ======================================================

    "normality_shapiro": {
        "label": "Teste de Normalidade (Shapiro-Wilk)",
        "requires": {
            "numeric": {
                "count": 1,
                "constraints": ["numeric"]
            }
        },
        "min_n": 3,
        "max_n": 5000,
        "description": "Avalia se os dados seguem distribuição normal."
    },

    # ======================================================
    # CORRELAÇÃO
    # ======================================================

    "correlation_matrix": {
        "label": "Matriz de Correlação",
        "requires": {
            "numeric": {
                "count": ">=2",
                "constraints": ["numeric"]
            }
        },
        "description": "Calcula correlação entre variáveis numéricas."
    },

    # ======================================================
    # REGRESSÃO
    # ======================================================

    "regression_linear_simple": {
        "label": "Regressão Linear Simples",
        "requires": {
            "x": {
                "count": 1,
                "constraints": ["numeric"]
            },
            "y": {
                "count": 1,
                "constraints": ["numeric"]
            }
        },
        "min_n": 3,
        "description": "Modela relação linear entre duas variáveis."
    },

    # ======================================================
    # SPC — GRÁFICOS DE CONTROLE
    # ======================================================

    "imr_chart": {
        "label": "Carta I-MR",
        "requires": {
            "numeric": {
                "count": 1,
                "constraints": ["numeric"]
            },
            "order": {
                "count": 0,
                "constraints": ["datetime_or_index"]
            }
        },
        "min_n": 5,
        "description": "Monitora estabilidade de processo para dados individuais."
    },

    "xbar_r_chart": {
        "label": "Carta Xbarra-R",
        "requires": {
            "numeric": {
                "count": 1,
                "constraints": ["numeric"]
            },
            "subgroup": {
                "count": 1,
                "constraints": ["categorical"]
            }
        },
        "parameters": {
            "subgroup_size": {
                "type": "int",
                "required": True
            }
        },
        "description": "Monitora média e variabilidade de subgrupos."
    },

    "p_chart": {
        "label": "Carta p",
        "requires": {
            "defectives": {
                "count": 1,
                "constraints": ["int_nonneg"]
            },
            "total": {
                "count": 1,
                "constraints": ["int_pos"]
            }
        },
        "constraints": [
            "defectives<=total"
        ],
        "description": "Monitora proporção de itens defeituosos."
    },

    "u_chart": {
        "label": "Carta u",
        "requires": {
            "defects": {
                "count": 1,
                "constraints": ["int_nonneg"]
            }
        },
        "description": "Monitora taxa média de defeitos por unidade."
    },
}
