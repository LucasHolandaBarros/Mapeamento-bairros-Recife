import pandas as pd
import unidecode
import sys
import csv
from pathlib import Path
from src.graphs.graph import Graph  # 🔧 Corrigido para import absoluto

# Caminho base
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def derreter_bairros(
    input_path: Path = BASE_DIR / "data" / "bairros_recife.csv",
    output_path: Path = BASE_DIR / "data" / "bairros_unique.csv"
):
    """
    Lê o CSV original com colunas de microrregiões (1.1 a 6.3),
    derrete (melt) em formato bairro → microrregião,
    padroniza acentuação e remove duplicatas.
    Mantém subdivisões apenas para 3.1, 3.2 e 3.3.
    """
    print(f"🔄 Processando arquivo de entrada: {input_path}")

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"🚨 Erro: Arquivo não encontrado em {input_path}", file=sys.stderr)
        return
    except Exception as e:
        print(f"🚨 Erro ao ler CSV: {e}", file=sys.stderr)
        return

    # 🔧 Derreter colunas (gera microrregiao e bairro)
    df_melt = df.melt(var_name="microrregiao", value_name="bairro")

    # Remover linhas vazias
    df_melt = df_melt.dropna(subset=["bairro"])

    # 🔧 Regra especial: manter 3.1, 3.2, 3.3
    def ajustar_microrregiao(valor):
        valor = str(valor).strip()
        if valor.startswith("3."):
            return valor  # mantém subdivisões 3.x
        return valor.split(".")[0]  # converte 1.2 → 1

    df_melt["microrregiao"] = df_melt["microrregiao"].apply(ajustar_microrregiao)

    # Padronizar nomes dos bairros
    df_melt["bairro"] = (
        df_melt["bairro"]
        .apply(lambda x: unidecode.unidecode(str(x).strip().title()))
    )

    # Remover duplicatas
    df_unique = df_melt.drop_duplicates(subset=["bairro"])
    df_unique = df_unique[["bairro", "microrregiao"]]

    # Salvar resultado
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_unique.to_csv(output_path, index=False, encoding="utf-8")
        print(f"✅ Arquivo '{output_path}' gerado com sucesso! ({len(df_unique)} bairros únicos)")
    except Exception as e:
        print(f"🚨 Erro ao salvar arquivo: {e}", file=sys.stderr)

    return df_unique


def load_graph_from_csvs() -> Graph:
    """
    Cria uma instância do Grafo e a popula com os dados dos CSVs:
    1. 'bairros_unique.csv' para os NÓS e seus atributos (microrregiao).
    2. 'adjacencias_bairros.csv' para as ARESTAS e seus atributos (peso, etc.).
    
    (Esta função é a do Passo 3 anterior, e ela é 100% compatível
     com seus CSVs normalizados em TitleCase)
    """
    
    # Caminhos para os arquivos
    nodes_file = BASE_DIR / "data" / "bairros_unique.csv"
    edges_file = BASE_DIR / "data" / "adjacencias_bairros.csv"
    
    g = Graph()
    
    # 1. Processa os NÓS (bairros_unique.csv)
    try:
        with open(nodes_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Adiciona o nó (ex: "Boa Viagem") com seu atributo
                g.add_node(row['bairro'], microrregiao=row['microrregiao'])
    except FileNotFoundError:
        print(f"🚨 Erro: Arquivo de nós não encontrado: {nodes_file}", file=sys.stderr)
        print("Execute 'python src/graphs/io.py' primeiro.", file=sys.stderr)
        sys.exit(1) # Sai do programa se não puder carregar os nós
        
    # 2. Processa as ARESTAS (adjacencias_bairros.csv)
    try:
        with open(edges_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Pega os atributos principais
                    # Seus CSVs já estão em TitleCase, então o match é direto.
                    u = row['bairro_origem']
                    v = row['bairro_destino']
                    
                    # Seus pesos são inteiros (1, 2, 4, 7), mas float() aceita
                    peso = float(row['peso']) 
                    
                    # Pega atributos extras (logradouro, observacao)
                    extra_attrs = row.copy()
                    del extra_attrs['bairro_origem']
                    del extra_attrs['bairro_destino']
                    del extra_attrs['peso']
                    
                    g.add_edge(u, v, weight=peso, **extra_attrs)
                    
                except KeyError as e:
                    print(f"🚨 Erro: Coluna ausente {e} em 'adjacencias_bairros.csv'", file=sys.stderr)
                except ValueError:
                    print(f"🚨 Erro: 'peso' inválido na linha: {row}", file=sys.stderr)
                except Exception:
                    # Linhas em branco no final do CSV, como ',,,,'
                    if row['bairro_origem'] == '' and row['bairro_destino'] == '':
                        continue # Ignora linha em branco
                    else:
                        print(f"🚨 Erro processando linha: {row}", file=sys.stderr)
                        
    except FileNotFoundError:
        print(f"🚨 Erro: Arquivo de arestas não encontrado: {edges_file}", file=sys.stderr)
        print("Certifique-se de que você criou este arquivo manualmente.", file=sys.stderr)
        sys.exit(1) # Sai se não puder carregar as arestas

    print(f"✅ Grafo carregado com sucesso.")
    print(f"   Ordem (|V|): {g.get_order()} nós (bairros)")
    print(f"   Tamanho (|E|): {g.get_size()} arestas (interconexões)")
    
    return g

# Teste rápido (roda a sua função se o arquivo for executado diretamente)
if __name__ == "__main__":
    derreter_bairros()