import pandas as pd
import numpy as np


def matriz_impacto_esforco(lista_solucoes):
    impacto = np.random.randint(2, 6, size=len(lista_solucoes))
    esforço = np.random.randint(1, 5, size=len(lista_solucoes))
    prioridade = impacto - 0.5 * esforço

    df = pd.DataFrame({
        "Solução": lista_solucoes,
        "Impacto": impacto,
        "Esforço": esforço,
        "Prioridade": prioridade
    })

    return df
