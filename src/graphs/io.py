import pandas as pd
import unidecode

def derreter_bairros(
    input_path="data/bairros_recife.csv",
    output_path="data/bairros_unique.csv"
):
    """
    Lê o CSV original com colunas de microrregiões (1.1 a 6.3),
    derrete (melt) em formato bairro → microrregião (1 a 6),
    padroniza acentuação e remove duplicatas.
    """
    # Ler o CSV
    df = pd.read_csv(input_path)

    # Derreter (unpivot): transforma colunas em linhas
    df_melt = df.melt(var_name="microrregiao", value_name="bairro")

    # Remover linhas vazias
    df_melt = df_melt.dropna(subset=["bairro"])

    # Extrair apenas o número inteiro da microrregião (antes do ponto)
    df_melt["microrregiao"] = df_melt["microrregiao"].apply(lambda x: str(x).split(".")[0])

    # Padronizar nome dos bairros (sem acento, caixa alta inicial)
    df_melt["bairro"] = (
        df_melt["bairro"]
        .apply(lambda x: unidecode.unidecode(x.strip().title()))
    )

    # Remover duplicatas
    df_unique = df_melt.drop_duplicates(subset=["bairro"])

    df_unique = df_unique[["bairro", "microrregiao"]]

    # Salvar resultado
    df_unique.to_csv(output_path, index=False, encoding="utf-8")

    print(f"✅ Arquivo '{output_path}' gerado com sucesso! ({len(df_unique)} bairros únicos)")

    return df_unique


# Teste rápido (roda se o arquivo for executado diretamente)
if __name__ == "__main__":
    derreter_bairros()
