import csv
import time
import json
from typing import Any, Dict, List, Set, Tuple, Optional

from graph import Graph
from algorithms import dijkstra
from algorithms import bfs, dfs
from viz import visualize_ego_network

def load_graph_from_csv(filepath: str) -> Graph:
    """
    Lê o CSV de voos e constrói o grafo dirigido e ponderado.
    """
    g = Graph()
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            count = 0
            for row in reader:
                try:
                    origem = row['Cidade_Estado_Origem']
                    destino = row['Cidade_Estado_Destino']
                    duracao = float(row['Duracao'])
                    
                    if duracao > 0:
                        g.add_directed_edge(
                            origem, 
                            destino, 
                            weight=duracao, 
                            companhia=row['Companhia.Aerea'],
                            voo=row['Voos']
                        )
                        count += 1
                        
                except (ValueError, TypeError, KeyError):
                    continue
                    
            print(f"--- Carregamento do Grafo Concluído ---")
            print(f"|V| (Cidades): {g.get_order()}")
            print(f"|E| (Voos):    {g.get_size()} (carregados {count})")
            print("------------------------------------------")
            
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{filepath}'")
        return g
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return g
        
    return g

# --- 4. EXECUÇÃO DOS TESTES (REQUISITO 2b) ---

if __name__ == "__main__":
    
    # 1. Carrega o grafo do seu CSV
    arquivo_csv = "Parte-2/dados/BrFlights2_filtrado.csv"
    grafo_voos = load_graph_from_csv(arquivo_csv)
    
    if grafo_voos.get_order() > 0:
        # ... (seu código do Dijkstra) ...
        
        # --- TESTE DA VISUALIZAÇÃO (Requisito 4) ---
        print("\n--- Gerando Visualizações ---")
        
        # Tente com um hub conhecido. Você pode precisar ajustar o nome
        # ex: "Guarulhos/SP", "Rio De Janeiro", "Brasilia"
        hub_principal = "Rio De Janeiro/RJ" 
        visualize_ego_network(grafo_voos, hub_principal, "rede_ego_rio.html")
    
    print("\n------------------------- Testando BFS -------------------------")
    fontes = ["Porto Alegre/RS", "Salvador/BA", "Guarulhos/SP"]
    print("Resultado BFS:\nPorto Alegre/RS", bfs(grafo_voos, "Porto Alegre/RS"))
    print("Brasilia/DF", bfs(grafo_voos, "Brasilia/DF"))
    print("Salvador/BA", bfs(grafo_voos, "Salvador/BA"))

    print("\n------------------------- Testando DFS -------------------------")
    fontes = ["Porto Alegre/RS", "Salvador/BA", "Guarulhos/SP"]
    print("Resultado DFS:\nPorto Alegre/RS", dfs(grafo_voos, "Porto Alegre/RS"))
    print("Brasilia/DF", dfs(grafo_voos, "Brasilia/DF"))
    print("Salvador/BA", dfs(grafo_voos, "Salvador/BA"))

