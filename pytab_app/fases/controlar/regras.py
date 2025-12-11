import numpy as np
import pandas as pd


def regra_ponto_fora_limite(valores, lcl, ucl):
    """
    Regra 1: pontos fora de LCL/UCL.
    Retorna DataFrame com índices e valores violados.
    """
    valores = pd.Series(valores)
    mask = (valores > ucl) | (valores < lcl)
    viol = valores[mask]
    df = pd.DataFrame({"index": viol.index, "valor": viol.values})
    df["regra"] = "Ponto fora dos limites (Regra 1)"
    return df


def regra_tendencia(valores, n_seq=6):
    """
    Regra de tendência: n_seq pontos sempre subindo ou sempre descendo.
    """
    valores = pd.Series(valores).reset_index(drop=True)
    diffs = np.diff(valores)

    up = diffs > 0
    down = diffs < 0

    violacoes = []

    # sequência de subida
    count = 0
    start = 0
    for i, flag in enumerate(up):
        if flag:
            if count == 0:
                start = i
            count += 1
            if count >= n_seq:
                violacoes.append((start, i + 1, "Tendência de subida (Regra 2)"))
        else:
            count = 0

    # sequência de descida
    count = 0
    start = 0
    for i, flag in enumerate(down):
        if flag:
            if count == 0:
                start = i
            count += 1
            if count >= n_seq:
                violacoes.append((start, i + 1, "Tendência de descida (Regra 2)"))
        else:
            count = 0

    if not violacoes:
        return pd.DataFrame(columns=["inicio", "fim", "regra"])

    return pd.DataFrame(violacoes, columns=["inicio", "fim", "regra"])


def regra_lado_media(valores, n_seq=8):
    """
    Regra: n_seq pontos consecutivos acima ou abaixo da média.
    """
    valores = pd.Series(valores)
    media = valores.mean()
    acima = valores > media
    abaixo = valores < media

    violacoes = []

    # acima
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

    # abaixo
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
