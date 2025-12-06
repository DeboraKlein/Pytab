"""
Testes básicos para o módulo pytab.io.reader
"""

import pandas as pd
from pytab.io.reader import read_csv_smart
import os


def test_read_csv_smart(tmp_path):
    # Cria um arquivo CSV temporário
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("a,b\n1,2\n3,4")

    df = read_csv_smart(str(csv_path))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
