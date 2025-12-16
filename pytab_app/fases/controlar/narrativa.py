from __future__ import annotations

from typing import Any


def _fmt(x: Any, nd: int = 2) -> str:
    try:
        v = float(x)
    except Exception:
        return "-"
    return f"{v:.{nd}f}".replace(".", ",")


def narrativa_imr(indicador_or_resumo, resumo: dict | None = None) -> str:
    """
    Compatível com:
      - narrativa_imr(resumo)
      - narrativa_imr(indicador, resumo)
    """
    if resumo is None:
        indicador = None
        resumo = indicador_or_resumo
    else:
        indicador = indicador_or_resumo

    viol_total = (
        resumo.get("violacoes_regra1", 0)
        + resumo.get("violacoes_regra2", 0)
        + resumo.get("violacoes_regra3", 0)
    )

    if viol_total == 0:
        estado = "O processo aparenta estar **estável e sob controle estatístico**."
    else:
        estado = (
            "Foram identificados indícios de **instabilidade** no processo. "
            "Recomenda-se investigar as causas especiais associadas aos pontos sinalizados."
        )

    titulo_indicador = f"**Indicador:** {indicador}\n\n" if indicador else ""

    return f"""
### Interpretação — Carta I-MR

{titulo_indicador}- Média do processo: **{_fmt(resumo.get('media'), 2)}**
- Desvio-padrão estimado: **{_fmt(resumo.get('sigma'), 2)}**
- Limites de controle (I): **LCL = {_fmt(resumo.get('lcl'), 2)}**, **UCL = {_fmt(resumo.get('ucl'), 2)}**
- Violação da Regra 1 (fora de LCL/UCL): **{resumo.get('violacoes_regra1', 0)}**
- Tendências (Regra 2): **{resumo.get('violacoes_regra2', 0)}**
- Sequências do mesmo lado da média (Regra 3): **{resumo.get('violacoes_regra3', 0)}**

{estado}
"""


def narrativa_xbar_r(indicador_or_resumo, resumo: dict | None = None) -> str:
    """
    Compatível com:
      - narrativa_xbar_r(resumo)
      - narrativa_xbar_r(indicador, resumo)
    """
    if resumo is None:
        indicador = None
        resumo = indicador_or_resumo
    else:
        indicador = indicador_or_resumo

    if resumo.get("violacoes_x", 0) == 0 and resumo.get("violacoes_r", 0) == 0:
        estado = "As médias e amplitudes dos subgrupos estão **consistentes e sob controle**."
    else:
        estado = (
            "Foram observadas violações nos gráficos de média e/ou amplitude. "
            "Isso sugere presença de causas especiais atuando em determinados subgrupos."
        )

    titulo_indicador = f"**Indicador:** {indicador}\n\n" if indicador else ""

    return f"""
### Interpretação — Carta X̄-R

{titulo_indicador}- Tamanho de subgrupo: **{resumo.get('n_subgrupo', '-') }**
- Média geral das médias (X̄̄): **{_fmt(resumo.get('xbar'), 2)}**
- Média das amplitudes (R̄): **{_fmt(resumo.get('rbar'), 2)}**
- Violação da Regra 1 em X̄: **{resumo.get('violacoes_x', 0)}**
- Violação da Regra 1 em R: **{resumo.get('violacoes_r', 0)}**

{estado}
"""


def narrativa_p(*args) -> str:
    """
    Compatível com:
      - narrativa_p(resumo)
      - narrativa_p(col_def, col_tot, resumo)
    """
    if len(args) == 1:
        col_def = None
        col_tot = None
        resumo = args[0]
    elif len(args) >= 3:
        col_def, col_tot, resumo = args[0], args[1], args[2]
    else:
        return "### Interpretação — Carta P\nParâmetros inválidos."

    if resumo.get("violacoes", 0) == 0:
        estado = "A proporção de defeituosos está **dentro dos limites esperados**."
    else:
        estado = (
            "Foram detectados pontos fora dos limites de controle na proporção de defeituosos. "
            "Isso indica possíveis períodos com desempenho significativamente pior."
        )

    rotulo = ""
    if col_def and col_tot:
        rotulo = f"**Defeituosos:** {col_def} | **Inspecionados:** {col_tot}\n\n"

    return f"""
### Interpretação — Carta P

{rotulo}- Proporção média de defeituosos (p̄): **{_fmt(resumo.get('p_bar'), 4)}**

{estado}
"""


def narrativa_u(*args) -> str:
    """
    Compatível com:
      - narrativa_u(resumo)
      - narrativa_u(col_def, col_opp, resumo)
    """
    if len(args) == 1:
        col_def = None
        col_opp = None
        resumo = args[0]
    elif len(args) >= 3:
        col_def, col_opp, resumo = args[0], args[1], args[2]
    else:
        return "### Interpretação — Carta U\nParâmetros inválidos."

    if resumo.get("violacoes", 0) == 0:
        estado = "O número de defeitos por unidade está **sob controle estatístico**."
    else:
        estado = (
            "Foram observados pontos fora de controle no número de defeitos por unidade. "
            "Recomenda-se investigar condições específicas nas amostras destacadas."
        )

    rotulo = ""
    if col_def and col_opp:
        rotulo = f"**Defeitos:** {col_def} | **Oportunidades:** {col_opp}\n\n"

    return f"""
### Interpretação — Carta U

{rotulo}- Média de defeitos por unidade (ū): **{_fmt(resumo.get('u_bar'), 4)}**

{estado}
"""

