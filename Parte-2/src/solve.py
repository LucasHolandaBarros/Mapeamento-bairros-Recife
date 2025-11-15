import csv
import time
import json
from typing import Any, Dict, List, Set, Tuple, Optional

from graph import Graph
from algorithms import dijkstra
from algorithms import bfs, dfs, bellman_ford, medir_desempenho
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
    arquivo_csv = "Mapeamento-bairros-Recife/Parte-2/dados/BrFlights2_filtrado.csv"
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

    print("\n------------------------- Testando Bellman-Ford -------------------------")

    report = {}
    # Calculando o tempo e memória de dijkstra antes de adicionar pesos negativos
    # Caso tivesse mais embaixo do código haveria a possibilidade do algoritmo quebrar o algoritmo
    caminho, tempo_dijkstra = medir_desempenho(dijkstra, grafo_voos, "Cascavel/PR", "Miami/N/I", medir_memoria=True)
    report['Dijkstra'] = tempo_dijkstra

    import json
    import os
    import math

    # Salvando o resultado no Json
    def save_bellman_json(resultado: dict, filename: str):
        def _sanitize_for_json(resultado: dict, float_precision: int = 6) -> dict:
            sanitized = {
                "distancias": {},
                "predecessores": resultado.get("predecessores", {}).copy(),
                "ha_ciclo_negativo": bool(resultado.get("ha_ciclo_negativo", False))
            }

            dist = resultado.get("distancias", {})
            for node, d in dist.items():
                if isinstance(d, (int, float)):
                    if not math.isfinite(d):
                        sanitized["distancias"][node] = None
                    else:
                        sanitized["distancias"][node] = round(float(d), float_precision)
                else:
                    sanitized["distancias"][node] = d

            return sanitized

        os.makedirs("Mapeamento-bairros-Recife/Parte-2/out", exist_ok=True)
        path_json = os.path.join("Mapeamento-bairros-Recife/Parte-2/out", filename)

        sanitized = _sanitize_for_json(resultado)
        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, indent=4, ensure_ascii=False, allow_nan=False)

        print(f"\n[INFO] Arquivo JSON gerado em: {path_json}")

    rotas_negativas = [
        ("Maceio/AL", "Miami/N/I", -5),
        ("Porto Velho/RO", "Paris/N/I", -4)
    ]

    rotas_negativas_ciclo = [
        ("Recife/PE", "Campina Grande/PB", -2),
        ("Campina Grande/PB", "João Pessoa/PB", -3),
        ("João Pessoa/PB", "Recife/PE", -1)  # ciclo negativo
    ]

    # Aplicando conexões negativas porém sem ciclo
    print("\n1. Bellman-Ford sem ciclo negativo")
    for u, v, peso in rotas_negativas:
        if u in grafo_voos.adj and v in grafo_voos.adj[u]:
            grafo_voos.adj[u][v]["weight"] = peso
            print(f"[INFO] Peso negativo aplicado na rota existente: {u} -> {v} ({peso})")
        else:
            grafo_voos.add_directed_edge(u, v, weight=peso)
            print(f"[INFO] Rota negativa criada: {u} -> {v} ({peso})")

    resultado_sem_ciclo = bellman_ford(grafo_voos, "Porto Alegre/RS")
    save_bellman_json(resultado_sem_ciclo, "bellman_ford_sem_ciclo_negativo.json")

    print("\n-----------------------===========================-----------------------")

    # Aplicando conexões negativas gerando ciclos negativos
    print("\n2. Bellman-Ford com ciclo negativo")
    for u, v, peso in rotas_negativas_ciclo:
        if u in grafo_voos.adj and v in grafo_voos.adj[u]:
            grafo_voos.adj[u][v]["weight"] = peso
            print(f"[INFO] Peso negativo aplicado na rota existente: {u} -> {v} ({peso})")
        else:
            grafo_voos.add_directed_edge(u, v, weight=peso)
            print(f"[INFO] Rota negativa criada: {u} -> {v} ({peso})")
    
    print("[INFO] ciclo: ")
    for u, v, peso in rotas_negativas_ciclo:
        print(f"{u} -> {v} ")

    resultado_com_ciclo = bellman_ford(grafo_voos, "Porto Alegre/RS")
    save_bellman_json(resultado_com_ciclo, "bellman_ford_com_ciclo_negativo.json")
    
    # --- BFS ---
    _, tempo_bfs = medir_desempenho(bfs, grafo_voos, "Cascavel/PR", medir_memoria=True)
    report['BFS'] = tempo_bfs

    # --- DFS ---
    _, tempo_dfs = medir_desempenho(dfs, grafo_voos, "Cascavel/PR", medir_memoria=True)
    report['DFS'] = tempo_dfs

    # --- Bellman-Ford ---
    _, tempo_bf = medir_desempenho(bellman_ford, grafo_voos, "Cascavel/PR", medir_memoria=True)
    report['Bellman-Ford'] = tempo_bf
    
    # --- salvar JSON ---
    import os, json
    os.makedirs("Mapeamento-bairros-Recife/Parte-2/out", exist_ok=True)
    with open("Mapeamento-bairros-Recife/Parte-2/out/parte2_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        

    print("\n-----------------------== Metricas de Desempenho ==-----------------------")
    print("\n[INFO] Relatório de métricas salvo em out/parte2_report.json")
    print("Analisando-se o caminho partindo de Cascavel/PR\n")
