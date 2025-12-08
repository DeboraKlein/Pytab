import streamlit as st
import pandas as pd


def fase_melhorar(df: pd.DataFrame, types: dict) -> None:
    st.markdown("## Fase I — Melhorar")
    st.write(
        """
Nesta fase, o foco é propor e testar melhorias no processo.

Em versões futuras, o PyTab poderá apoiar você com:
- comparação antes/depois (baseline vs. pós-melhoria),
- estimativa de impacto na média e na variabilidade,
- cenários simples "e se" para apoiar decisões.

Por enquanto, você pode:
- usar as medições atuais como baseline,
- exportar os resultados,
- e comparar com novas rodadas de dados após a implementação das melhorias.
"""
    )
