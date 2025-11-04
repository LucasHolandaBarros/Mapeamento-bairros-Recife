import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
import csv # <--- NOVA IMPORTAÇÃO
import sys

# --- NOVAS IMPORTAÇÕES ---
from graphs.io import load_graph_from_csvs
from graphs.algorithms import dijkstra

# Define o caminho base e o diretório de saída
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "out"

def calculate_global_metrics(g):
    """Calcula métricas globais (Parte 3)"""
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
    """Calcula métricas por microrregião (Parte 3)"""
    print("🌍 Calculando métricas por microrregião...")
    bairros_por_micro = defaultdict(list)
    for node in g.get_nodes():
        attrs = g.get_node_attributes(node)
        microrregiao = attrs.get('microrregiao', 'desconhecida')
        bairros_por_micro[microrregiao].append(node)
        
    results = []
    for microrregiao, bairros in bairros_por_micro.items():
        subgraph = g.get_induced_subgraph(bairros)
        results.append({
            'microrregiao': microrregiao,
            'bairros_count': len(bairros),
            'ordem_subgrafo': subgraph.get_order(),
            'tamanho_subgrafo': subgraph.get_size(),
            'densidade_subgrafo': subgraph.get_density()
        })
        
    output_file = OUTPUT_DIR / "microrregioes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✅ Métricas de microrregiões salvas em: {output_file}")

def calculate_ego_metrics_and_rankings(g):
    """Calcula métricas de ego-network (Parte 3) e rankings (Parte 4)"""
    print("👤 Calculando métricas de ego-network e rankings...")
    results = []
    for bairro in sorted(g.get_nodes()):
        grau = g.get_degree(bairro)
        ego_network = g.get_ego_network(bairro)
        results.append({
            'bairro': bairro,
            'grau': grau,
            'ordem_ego': ego_network.get_order(),
            'tamanho_ego': ego_network.get_size(),
            'densidade_ego': ego_network.get_density()
        })
        
    df = pd.DataFrame(results)
    
    # Salva ego_bairro.csv (Parte 3)
    output_file_ego = OUTPUT_DIR / "ego_bairro.csv"
    df.to_csv(output_file_ego, index=False, encoding='utf-8')
    print(f"✅ Métricas de ego-network salvas em: {output_file_ego}")

    # Salva graus.csv (Parte 4)
    df_graus = df[['bairro', 'grau']].sort_values(by='grau', ascending=False)
    output_file_graus = OUTPUT_DIR / "graus.csv"
    df_graus.to_csv(output_file_graus, index=False, encoding='utf-8')
    print(f"✅ Lista de graus salva em: {output_file_graus}")
    
    # Imprime rankings (Parte 4)
    if not df_graus.empty:
        bairro_maior_grau = df_graus.iloc[0]
        print(f"🏆 Bairro com MAIOR GRAU: {bairro_maior_grau['bairro']} (Grau: {bairro_maior_grau['grau']})")
    
    df_densidade = df.sort_values(by='densidade_ego', ascending=False)
    if not df_densidade.empty:
        bairro_mais_denso = df_densidade.iloc[0]
        print(f"🏆 Bairro MAIS DENSO (Ego-Network): {bairro_mais_denso['bairro']} (Densidade: {bairro_mais_denso['densidade_ego']:.4f})")

# --- NOVA FUNÇÃO (PARTE 6) ---
def calculate_address_distances(g):
    """
    Lê o arquivo 'data/enderecos.csv' e calcula o caminho mais curto
    entre os bairros correspondentes usando Dijkstra.
    Salva 'out/distancias_enderecos.csv' e o percurso especial.
    """
    print("🗺️  Calculando distâncias entre endereços (Dijkstra)...")
    
    input_file = BASE_DIR / "data" / "enderecos.csv"
    output_file_csv = OUTPUT_DIR / "distancias_enderecos.csv"
    output_file_json = OUTPUT_DIR / "percurso_nova_descoberta_setubal.json"
    
    results = []
    mandatory_pair_path = {}
    
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    x, y = row['X'], row['Y']
                    bairro_x_raw, bairro_y_raw = row['bairro_X'], row['bairro_Y']
                    
                    # 1. Normaliza os nomes dos bairros
                    # Usamos a função de io.py para consistência
                    bairro_x = bairro_x_raw
                    bairro_y = bairro_y_raw
                    
                    # 2. Aplica a REGRA DE SETÚBAL
                    if bairro_x == "Setúbal": bairro_x = "Boa Viagem"
                    if bairro_y == "Setúbal": bairro_y = "Boa Viagem"
                        
                    # 3. Executa Dijkstra
                    if bairro_x not in g.nodes:
                        print(f"🚨 Aviso: Bairro de origem '{bairro_x_raw}' (normalizado para '{bairro_x}') não encontrado no grafo.", file=sys.stderr)
                        cost, path = float('inf'), []
                    elif bairro_y not in g.nodes:
                        print(f"🚨 Aviso: Bairro de destino '{bairro_y_raw}' (normalizado para '{bairro_y}') não encontrado no grafo.", file=sys.stderr)
                        cost, path = float('inf'), []
                    else:
                        cost, path = dijkstra(g, bairro_x, bairro_y)
                        
                    # 4. Salva o resultado
                    results.append({
                        'X': x,
                        'Y': y,
                        'bairro_X': bairro_x_raw,
                        'bairro_Y': bairro_y_raw,
                        'custo': cost,
                        'caminho': " -> ".join(path) # Formato "A -> B -> C"
                    })
                    
                    # 5. Verifica o par obrigatório
                    # Compara com os nomes *originais* do CSV
                    if bairro_x_raw == "Nova Descoberta" and bairro_y_raw == "Setúbal":
                        mandatory_pair_path = {
                            'bairro_X': bairro_x_raw,
                            'bairro_Y': bairro_y_raw,
                            'custo': cost, 
                            'caminho': path}
                        
                except KeyError as e:
                    print(f"🚨 Erro: Coluna ausente {e} em 'enderecos.csv'", file=sys.stderr)
                    
    except FileNotFoundError:
        print(f"🚨 Erro: Arquivo de endereços não encontrado: {input_file}", file=sys.stderr)
        print("Crie 'data/enderecos.csv' manualmente.", file=sys.stderr)
        return # Aborta esta função se o arquivo não existir

    # Salva o CSV com todos os pares
    if results:
        df_dist = pd.DataFrame(results)
        df_dist.to_csv(output_file_csv, index=False, encoding='utf-8')
        print(f"✅ Distâncias de endereços salvas em: {output_file_csv}")

    # Salva o JSON do par obrigatório
    if mandatory_pair_path:
        with open(output_file_json, 'w', encoding='utf-8') as f:
            json.dump(mandatory_pair_path, f, indent=2, ensure_ascii=False)
        print(f"✅ Percurso obrigatório salvo em: {output_file_json}")
    else:
        print("⚠️ Aviso: Par obrigatório 'Nova Descoberta -> Setúbal' não encontrado em 'enderecos.csv'.")


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
    calculate_ego_metrics_and_rankings(graph)
    
    # --- CHAMADA DA NOVA FUNÇÃO (PARTE 6) ---
    calculate_address_distances(graph)
    
    print("\n🎉 Todos os cálculos foram concluídos e salvos na pasta 'out/'.")

if __name__ == "__main__":
    main()


