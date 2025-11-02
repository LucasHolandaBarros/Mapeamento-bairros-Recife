import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
from graphs.io import load_graph_from_csvs
import sys # Importação do sys (que corrigimos no passo anterior)

# Define o caminho base e o diretório de saída
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "out"

def calculate_global_metrics(g):
    """Calcula métricas globais e salva em out/recife_global.json"""
    print("📊 Calculando métricas globais...")
    metrics = {
        'ordem': g.get_order(),
        'tamanho': g.get_size(),
        'densidade': g.get_density()
    }
    
    output_file = OUTPUT_DIR / "recife_global.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Métricas globais salvas em: {output_file}")

def calculate_microrregiao_metrics(g):
    """Calcula métricas por microrregião e salva em out/microrregioes.json"""
    print("🌍 Calculando métricas por microrregião...")
    
    # 1. Agrupa bairros por microrregião
    bairros_por_micro = defaultdict(list)
    for node in g.get_nodes():
        attrs = g.get_node_attributes(node)
        microrregiao = attrs.get('microrregiao', 'desconhecida')
        bairros_por_micro[microrregiao].append(node)
        
    # 2. Calcula métricas para o subgrafo de cada microrregião
    results = []
    for microrregiao, bairros in bairros_por_micro.items():
        subgraph = g.get_induced_subgraph(bairros)
        
        ordem = subgraph.get_order()
        tamanho = subgraph.get_size()
        densidade = subgraph.get_density()
        
        results.append({
            'microrregiao': microrregiao,
            'bairros_count': len(bairros), # Ordem do subgrafo
            'ordem_subgrafo': ordem,       # Confirmação da ordem
            'tamanho_subgrafo': tamanho,   # Arestas *dentro* da microrregiao
            'densidade_subgrafo': densidade
        })
        
    # 3. Salva o resultado
    output_file = OUTPUT_DIR / "microrregioes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Métricas de microrregiões salvas em: {output_file}")

# --- FUNÇÃO ATUALIZADA (PARTE 3 + PARTE 4) ---
def calculate_ego_metrics_and_rankings(g):
    """
    Calcula métricas de ego-network para cada bairro (Parte 3)
    E também calcula os rankings de grau e densidade (Parte 4).
    """
    print("👤 Calculando métricas de ego-network e rankings...")
    
    results = []
    
    # Itera por todos os bairros em ordem alfabética
    for bairro in sorted(g.get_nodes()):
        grau = g.get_degree(bairro)
        ego_network = g.get_ego_network(bairro)
        
        ordem_ego = ego_network.get_order()
        tamanho_ego = ego_network.get_size()
        densidade_ego = ego_network.get_density()
        
        results.append({
            'bairro': bairro,
            'grau': grau,
            'ordem_ego': ordem_ego,
            'tamanho_ego': tamanho_ego,
            'densidade_ego': densidade_ego
        })
        
    # Converte resultados para DataFrame
    df = pd.DataFrame(results)
    
    # --- REQUISITO PARTE 3 (ego_bairro.csv) ---
    output_file_ego = OUTPUT_DIR / "ego_bairro.csv"
    df.to_csv(output_file_ego, index=False, encoding='utf-8')
    print(f"✅ Métricas de ego-network salvas em: {output_file_ego}")

    # --- REQUISITOS PARTE 4 (graus.csv e rankings) ---
    
    # 1. Gerar out/graus.csv
    # Seleciona, ordena pelo grau (descendente) e salva
    df_graus = df[['bairro', 'grau']].sort_values(by='grau', ascending=False)
    output_file_graus = OUTPUT_DIR / "graus.csv"
    df_graus.to_csv(output_file_graus, index=False, encoding='utf-8')
    print(f"✅ Lista de graus salva em: {output_file_graus}")
    
    # 2. Bairro com maior grau
    # Pega a primeira linha do DataFrame ordenado
    if not df_graus.empty:
        bairro_maior_grau = df_graus.iloc[0]
        print(f"🏆 Bairro com MAIOR GRAU: {bairro_maior_grau['bairro']} (Grau: {bairro_maior_grau['grau']})")
    
    # 3. Bairro mais denso (da ego-network)
    # Ordena o DataFrame original pela densidade_ego
    df_densidade = df.sort_values(by='densidade_ego', ascending=False)
    
    if not df_densidade.empty:
        bairro_mais_denso = df_densidade.iloc[0]
        print(f"🏆 Bairro MAIS DENSO (Ego-Network): {bairro_mais_denso['bairro']} (Densidade: {bairro_mais_denso['densidade_ego']:.4f})")

def main():
    """Função principal para carregar o grafo e executar todos os cálculos."""
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        graph = load_graph_from_csvs()
    except SystemExit:
        print("❌ Falha ao carregar o grafo. Abortando cálculos.", file=sys.stderr)
        return
        
    if graph.get_order() == 0:
        print("⚠️ O grafo está vazio. Verifique seus arquivos CSV.", file=sys.stderr)
        return

    # Executa os cálculos das Partes 3 e 4
    calculate_global_metrics(graph)
    calculate_microrregiao_metrics(graph)
    
    # Chamada da função atualizada
    calculate_ego_metrics_and_rankings(graph) 
    
    print("\n🎉 Todos os cálculos foram concluídos e salvos na pasta 'out/'.")

if __name__ == "__main__":
    main()