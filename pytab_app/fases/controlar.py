import streamlit as st
import pandas as pd


def fase_controlar(df: pd.DataFrame, types: dict) -> None:
    st.markdown("## Fase C — Controlar")
    st.write(
        """
Na fase de Controle, o objetivo é **garantir que os ganhos sejam sustentados**.

Versões futuras do PyTab poderão incluir:
- gráficos de controle (Ex.: XmR, X̄-R),
- monitoramento contínuo do indicador,
- alertas simples quando o processo sair do padrão.

Por enquanto, você pode:
- acompanhar regularmente o indicador usando a fase **Medir**,
- comparar novas medições com o baseline,
- e usar os gráficos para verificar se o processo continua estável.
"""
    )
