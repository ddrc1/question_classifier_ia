import pandas as pd
from statsmodels.stats.proportion import proportion_confint

df_publicacao: pd.DataFrame = pd.read_csv("./publicacao_v1.csv", usecols=["id", "decisao", "extras_ids", "confianca"])
df_referencia: pd.DataFrame = pd.read_csv("./referencia.csv", usecols=["id", "decisao", "extras_ids"])

limiar = 0.85
df_publicacao = df_publicacao[df_publicacao["confianca"] >= limiar]
df_merge: pd.DataFrame = df_publicacao.merge(df_referencia, on="id", how="inner", suffixes=("_publicacao", "_referencia"))
df_merge.fillna(-1, inplace=True)

df_acertos = df_merge[(df_merge["decisao_publicacao"] == df_merge["decisao_referencia"]) & (df_merge["extras_ids_publicacao"] == df_merge["extras_ids_referencia"])]

acertos, n = len(df_acertos), len(df_merge)
print(acertos, n)

precisao = acertos / n
low, high = proportion_confint(acertos, n, method="wilson")

print(low, high)
