import numpy as np
import pandas as pd


def regra_ponto_fora_limite(valores, lcl, ucl):
    """
    Regra 1: pontos fora dos limites de controle (LCL/UCL).

    Retorna DataFrame com:
      - index
      - valor
      - regra
    """
    valores = pd.Series(valores)

    # lcl / ucl podem ser escalares ou vetores
    if np.ndim(lcl):
        lcl_s = np.asarray(lcl)
    else:
        lcl_s = np.full_like(valores, lcl, dtype=float)

    if np.ndim(ucl):
        ucl_s = np.asarray(ucl)
    else:
        ucl_s = np.full_like(valores, ucl, dtype=float)

    mask = (valores > ucl_s) | (valores < lcl_s)
    viol = valores[mask]

    if viol.empty:
        return pd.DataFrame(columns=["index", "valor", "regra"])

    df = pd.DataFrame(
        {
            "index": viol.index,
            "valor": viol.values,
            "regra": ["Ponto fora dos limites (Regra 1)"] * len(viol),
        }
    )
    return df


def regra_tendencia(valores, n_seq: int = 6):
    """
    Regra 2: tendência – N pontos consecutivos subindo ou descendo.
    """
    valores = pd.Series(valores).astype(float)
    diffs = np.sign(np.diff(valores))

    violacoes = []
    count = 1
    direcao_atual = 0

    for i in range(1, len(valores)):
        if diffs[i - 1] == 0:
            count = 1
            direcao_atual = 0
            continue

        if diffs[i - 1] == direcao_atual:
            count += 1
        else:
            direcao_atual = diffs[i - 1]
            count = 2  # (i-1, i)

        if count >= n_seq:
            inicio = i - n_seq + 1
            fim = i
            violacoes.append((inicio, fim, "Tendência (Regra 2)"))

    if not violacoes:
        return pd.DataFrame(columns=["inicio", "fim", "regra"])

    return pd.DataFrame(violacoes, columns=["inicio", "fim", "regra"])


def regra_lado_media(valores, n_seq: int = 8):
    """
    Regra 3: N pontos consecutivos do mesmo lado da média.
    """
    valores = pd.Series(valores).astype(float)
    media = valores.mean()
    acima = valores > media
    abaixo = valores < media

    violacoes = []

    # Sequência acima da média
    count = 0
    start = 0
    for i, flag in enumerate(acima):
        if flag:
            if count == 0:
                start = i
            count += 1
            if count >= n_seq:
                violacoes.append((start, i, "Pontos consecutivos acima da média (Regra 3)"))
        else:
            count = 0

    # Sequência abaixo da média
    count = 0
    start = 0
    for i, flag in enumerate(abaixo):
        if flag:
            if count == 0:
                start = i
            count += 1
            if count >= n_seq:
                violacoes.append((start, i, "Pontos consecutivos abaixo da média (Regra 3)"))
        else:
            count = 0

    if not violacoes:
        return pd.DataFrame(columns=["inicio", "fim", "regra"])

    return pd.DataFrame(violacoes, columns=["inicio", "fim", "regra"])
