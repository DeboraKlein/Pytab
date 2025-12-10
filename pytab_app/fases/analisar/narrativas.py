def gerar_narrativa_correlacao(summary: dict | None) -> str:
    if not summary:
        return "Não foi possível identificar correlações relevantes com os dados atuais."

    v1 = summary["var1"]
    v2 = summary["var2"]
    r = summary["corr"]
    abs_r = abs(r)

    if abs_r < 0.3:
        intensidade = "fraca"
    elif abs_r < 0.6:
        intensidade = "moderada"
    else:
        intensidade = "forte"

    if r > 0:
        sentido = "positiva"
    else:
        sentido = "negativa"

    return (
        f"A relação mais forte observada foi entre **{v1}** e **{v2}** "
        f"(correlação {sentido}, {intensidade}, r ≈ {r:.2f}). "
        "Isso indica que variações em uma dessas variáveis tendem a estar associadas a variações na outra. "
        "Essa informação pode ser útil para investigar causas raiz ou efeitos indiretos no processo."
    )


def gerar_narrativa_pareto(summary: dict | None) -> str:
    if not summary:
        return "Não foi possível gerar uma narrativa de Pareto com os dados atuais."

    dim = summary["dimensao"]
    met = summary["metricao"]
    top_cats = summary["top_categorias"]
    share = summary["top_share"]
    n_top = summary["n_top"]

    lista = ", ".join(str(c) for c in top_cats)

    return (
        f"Na análise de Pareto de **{met}** por **{dim}**, "
        f"as {n_top} principais categorias ({lista}) concentram aproximadamente {share:.1f}% do total. "
        "Essas categorias são candidatas naturais para priorização em ações de melhoria, "
        "pois representam a maior parte do impacto observado."
    )


def gerar_narrativa_regressao(summary: dict | None) -> str:
    if not summary:
        return "Não foi possível ajustar um modelo de regressão confiável com os dados atuais."

    x = summary["x"]
    y = summary["y"]
    a = summary["coef_angular"]
    b = summary["intercepto"]
    r2 = summary["r2"]

    if r2 < 0.2:
        explicacao = "o modelo explica apenas uma pequena parte da variação observada"
    elif r2 < 0.5:
        explicacao = "o modelo explica uma parte moderada da variação observada"
    else:
        explicacao = "o modelo explica uma parcela relevante da variação observada"

    direcao = "aumenta" if a > 0 else "diminui"

    return (
        f"O modelo de regressão linear simples ajustado para **{y}** em função de **{x}** apresentou "
        f"R² ≈ {r2:.2f}, indicando que {explicacao}. "
        f"Em média, a cada aumento de uma unidade em **{x}**, **{y}** tende a {direcao} em cerca de {abs(a):.2f} unidades. "
        "Essa relação pode ser usada para estimativas aproximadas e para discutir quais variáveis têm maior influência sobre o indicador."
    )
