import csv
import json
from typing import Any, Dict, List, Set, Tuple, Optional
import json
import os
import math
import pandas as pd
from pathlib import Path
from .graph import Graph
from .algorithms import dijkstra
from .algorithms import bfs, dfs, bellman_ford, medir_desempenho
from .viz import visualize_ego_network

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "out"

# ------------------------------------------------------------------------------------------- #
#PARA EXECUTAR O SCRIPT, ENTRE NA PASTA "Parte-2" E DIGITE "python -m src.solve"
# ------------------------------------------------------------------------------------------- #

def load_graph_from_csv(filepath: str) -> Graph:
    """
    Lê o CSV de voos e constrói o grafo dirigido e ponderado.
    """
    g = Graph()
    dados = "dados/cidades_paises_unicos.csv"

    try:
        with open(dados, mode='r', encoding='utf-8') as f:
            reader1 = csv.DictReader(f)

            for row in reader1:
                g.add_node(row['Cidade_Estado'], Pais=row['Pais'])


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
                    
            print(f"\n--- Carregamento do Grafo Concluído ---")
            print(f"|V| (Cidades): {g.get_order()}")
            print(f"|E| (Voos):    {g.get_size()} (carregados {count})")
            print("Esse grafo é um grafo dirigido e ponderado")
            print("------------------------------------------")
            
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{filepath}'")
        return g
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return g
        
    return g

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

    os.makedirs("out", exist_ok=True)
    path_json = os.path.join("out", filename)

    sanitized = _sanitize_for_json(resultado)
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(sanitized, f, indent=4, ensure_ascii=False, allow_nan=False)

    print(f"\n[INFO] Arquivo JSON gerado em: {path_json}")

def visualize_graus(g):

    results = []
    for cidade_estado in sorted(g.get_nodes()):
        grau = g.get_out_degree(cidade_estado)
        ego_network = g.get_ego_network(cidade_estado)
        results.append({
            'cidade_estado': cidade_estado,
            'grau': grau,
        })

    df = pd.DataFrame(results)

    df_graus = df[['cidade_estado', 'grau']].sort_values(by='grau', ascending=False)
    output_file_graus = OUTPUT_DIR / "graus.csv"
    df_graus.to_csv(output_file_graus, index=False, encoding='utf-8')
    print(f"✅ Lista de graus salva em: {output_file_graus}")


if __name__ == "__main__":
    
    # 1. Carrega o grafo do seu CSV
    arquivo_csv = "dados/BrFlights2_filtrado.csv"
    grafo_voos = load_graph_from_csv(arquivo_csv)
    visualize_graus(grafo_voos)
    
    if grafo_voos.get_order() > 0:
        print("\n--- Gerando Visualizações ---")
        
     
        hub_principal = "Guarulhos/SP" 
        visualize_ego_network(grafo_voos , "Relation_Voos.html")

    print("\n------------------------- Testando Dijkstra -------------------------")
    print(dijkstra(grafo_voos, "Porto Alegre/RS", "Toronto/N/I"))
    print(dijkstra(grafo_voos, "Recife/PE", "Buenos Aires/N/I"))
    print(dijkstra(grafo_voos, "Dallas/Fort Worth/N/I", "Sao Paulo/SP"))
    
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
    with open("out/parte2_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        

    print("\n-----------------------== Metricas de Desempenho ==-----------------------")
    print("\n[INFO] Relatório de métricas salvo em out/parte2_report.json")
    print("Analisando-se o caminho partindo de Cascavel/PR\n")

