def narrativa_imr(resumo: dict) -> str:
    viol_total = (
        resumo["violacoes_regra1"]
        + resumo["violacoes_regra2"]
        + resumo["violacoes_regra3"]
    )

    if viol_total == 0:
        estado = "O processo aparenta estar **estável e sob controle estatístico**."
    else:
        estado = (
            "Foram identificados indícios de **instabilidade** no processo. "
            "Recomenda-se investigar as causas especiais associadas aos pontos sinalizados."
        )

    return f"""
### Interpretação — Carta I-MR

- Média do processo: **{resumo['media']:.2f}**
- Desvio-padrão estimado: **{resumo['sigma']:.2f}**
- Limites de controle (I): **LCL = {resumo['lcl']:.2f}**, **UCL = {resumo['ucl']:.2f}**
- Violação da Regra 1 (fora de LCL/UCL): **{resumo['violacoes_regra1']}**
- Tendências (Regra 2): **{resumo['violacoes_regra2']}**
- Sequências de pontos do mesmo lado da média (Regra 3): **{resumo['violacoes_regra3']}**

{estado}
"""


def narrativa_xbar_r(resumo: dict) -> str:
    if resumo["violacoes_x"] == 0 and resumo["violacoes_r"] == 0:
        estado = "As médias e amplitudes dos subgrupos estão **consistentes e sob controle**."
    else:
        estado = (
            "Foram observadas violações nos gráficos de média e/ou amplitude. "
            "Isso sugere presença de causas especiais atuando em determinados subgrupos."
        )

    return f"""
### Interpretação — Carta X̄-R

- Tamanho de subgrupo: **{resumo['n_subgrupo']}**
- Média geral das médias (X̄̄): **{resumo['xbar']:.2f}**
- Média das amplitudes (R̄): **{resumo['rbar']:.2f}**
- Violação da Regra 1 em X̄: **{resumo['violacoes_x']}**
- Violação da Regra 1 em R: **{resumo['violacoes_r']}**

{estado}
"""


def narrativa_p(resumo: dict) -> str:
    if resumo["violacoes"] == 0:
        estado = "A proporção de defeituosos está **dentro dos limites esperados**."
    else:
        estado = (
            "Foram detectados pontos fora dos limites de controle na proporção de defeituosos. "
            "Isso indica possíveis períodos com desempenho significativamente pior."
        )

    return f"""
### Interpretação — Carta P

- Proporção média de defeituosos (p̄): **{resumo['p_bar']:.4f}**

{estado}
"""


def narrativa_u(resumo: dict) -> str:
    if resumo["violacoes"] == 0:
        estado = "O número de defeitos por unidade está **sob controle estatístico**."
    else:
        estado = (
            "Foram observados pontos fora de controle no número de defeitos por unidade. "
            "Recomenda-se investigar condições específicas nas amostras destacadas."
        )

    return f"""
### Interpretação — Carta U

- Média de defeitos por unidade (ū): **{resumo['u_bar']:.4f}**

{estado}
"""
