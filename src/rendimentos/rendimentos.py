import xml.etree.cElementTree as et
from pathlib import Path

import pandas as pd

from src.models import (
    DadosEconomicoFinanceiros,
)


def format_dados_gerais(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df["data_base"] = pd.to_datetime(df["data_base"], format="%Y-%m-%d")

    df = df.drop(["responsavel_informacao", "telefone_contato"], axis=1)

    df = df.sort_values(
        by=["cnpj_fundo", "cod_negociacao_cota", "data_base"], ascending=[True, True, False]
    )

    deduplicated_df = df.drop_duplicates(
        subset=["cnpj_fundo", "cod_negociacao_cota"], keep="first"
    ).copy()

    deduplicated_df["ativo"] = False

    idx_max_date = deduplicated_df.groupby("cnpj_fundo")["data_base"].idxmax()
    deduplicated_df.loc[idx_max_date, "ativo"] = True

    return deduplicated_df


if __name__ == "__main__":
    vals = []
    for path in Path("rendimentos").iterdir():
        tree = et.parse(path)
        root = tree.getroot()
        dados = DadosEconomicoFinanceiros.from_xml(root)

        if not dados.informe_rendimentos.rendimento:
            continue

        vals.append(
            {
                **dados.dados_gerais.model_dump(exclude_none=True),
                **{"data_base": dados.informe_rendimentos.rendimento.data_base},
            }
        )

    df = pd.DataFrame.from_records(vals)
    df = format_dados_gerais(df)
    print(df["cnpj_fundo"].value_counts())
    print(df.info())
    print(df[df["cnpj_fundo"] == "18085673000157"].head())
