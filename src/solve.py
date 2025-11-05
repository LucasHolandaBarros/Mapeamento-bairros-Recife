import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
import csv
import sys
from importlib import import_module

# --- IMPORTAÇÕES ATUALIZADAS ---
from graphs.io import load_graph_from_csvs, normalize_bairro_name
from graphs.algorithms import dijkstra
from viz import visualize_path
from viz import visualize_microrregioes
from viz import gerar_visualizacao_interativa

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

    output_file_ego = OUTPUT_DIR / "ego_bairro.csv"
    df.to_csv(output_file_ego, index=False, encoding='utf-8')
    print(f"✅ Métricas de ego-network salvas em: {output_file_ego}")

    df_graus = df[['bairro', 'grau']].sort_values(by='grau', ascending=False)
    output_file_graus = OUTPUT_DIR / "graus.csv"
    df_graus.to_csv(output_file_graus, index=False, encoding='utf-8')
    print(f"✅ Lista de graus salva em: {output_file_graus}")

    if not df_graus.empty:
        bairro_maior_grau = df_graus.iloc[0]
        print(f"🏆 Bairro com MAIOR GRAU: {bairro_maior_grau['bairro']} (Grau: {bairro_maior_grau['grau']})")

    df_densidade = df.sort_values(by='densidade_ego', ascending=False)
    if not df_densidade.empty:
        bairro_mais_denso = df_densidade.iloc[0]
        print(f"🏆 Bairro MAIS DENSO (Ego-Network): {bairro_mais_denso['bairro']} (Densidade: {bairro_mais_denso['densidade_ego']:.4f})")


def calculate_address_distances(g):
    """(Parte 6) Calcula caminhos de endereços e gera visualização"""
    print("🗺️  Calculando distâncias entre endereços (Dijkstra)...")

    input_file = BASE_DIR / "data" / "enderecos.csv"
    output_file_csv = OUTPUT_DIR / "distancias_enderecos.csv"
    output_file_json = OUTPUT_DIR / "percurso_nova_descoberta_setubal.json"
    output_file_html = OUTPUT_DIR / "arvore_percurso.html"

    results = []
    mandatory_pair_data = {}

    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    bairro_x_raw, bairro_y_raw = row['bairro_X'], row['bairro_Y']
                    bairro_x = normalize_bairro_name(bairro_x_raw)
                    bairro_y = normalize_bairro_name(bairro_y_raw)
                    if bairro_x == "Setubal": bairro_x = "Boa Viagem"
                    if bairro_y == "Setubal": bairro_y = "Boa Viagem"

                    if bairro_x not in g.nodes or bairro_y not in g.nodes:
                        cost, path = float('inf'), []
                    else:
                        cost, path = dijkstra(g, bairro_x, bairro_y)

                    results.append({
                        'bairro_X': bairro_x_raw, 'bairro_Y': bairro_y_raw,
                        'custo': cost, 'caminho': " -> ".join(path)
                    })

                    if bairro_x_raw == "Nova Descoberta" and bairro_y_raw == "Setúbal":
                        mandatory_pair_data = {'bairro_X': bairro_x_raw, 'bairro_Y': bairro_y_raw, 'custo': cost, 'caminho': path}

                except KeyError as e:
                    print(f"🚨 Erro: Coluna ausente {e}", file=sys.stderr)

    except FileNotFoundError:
        print(f"🚨 Erro: Arquivo de endereços não encontrado: {input_file}", file=sys.stderr)
        return

    if results:
        pd.DataFrame(results).to_csv(output_file_csv, index=False, encoding='utf-8')
        print(f"✅ Distâncias salvas em: {output_file_csv}")

    if mandatory_pair_data:
        with open(output_file_json, 'w', encoding='utf-8') as f:
            json.dump(mandatory_pair_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Percurso obrigatório salvo em: {output_file_json}")

        path_list = mandatory_pair_data.get('caminho', [])
        if path_list:
            visualize_path(g, path_list, output_file_html)
        else:
            print("⚠️ Nenhum caminho encontrado para visualização.")


def export_microrregioes_graphs(g):
    """Exporta subgrafos de microrregiões"""
    print("🧠 Exportando subgrafos por microrregião...")

    bairros_por_micro = defaultdict(list)
    for node in g.get_nodes():
        attrs = g.get_node_attributes(node)
        microrregiao = attrs.get('microrregiao', 'desconhecida')
        bairros_por_micro[microrregiao].append(node)

    microrregioes_data = {}
    for microrregiao, bairros in bairros_por_micro.items():
        subgraph = g.get_induced_subgraph(bairros)
        nodes_data = [{"id": n, "label": n} for n in subgraph.get_nodes()]
        edges_data = []
        for u in subgraph.get_nodes():
            for v, attrs in subgraph.adj[u].items():
                if u < v:
                    edges_data.append({"from": u, "to": v, "weight": attrs.get("weight", 1.0)})
        microrregioes_data[microrregiao] = {"nodes": nodes_data, "edges": edges_data}

    output_file = OUTPUT_DIR / "microrregioes_graphs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(microrregioes_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Subgrafos exportados em: {output_file}")


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

    calculate_global_metrics(graph)
    calculate_microrregiao_metrics(graph)
    calculate_ego_metrics_and_rankings(graph)
    export_microrregioes_graphs(graph)

    # ------------------------------------------------------------------
    # 🔹 NOVO BLOCO: Gerar o HTML interativo completo (generate_interactive_html)
    # ------------------------------------------------------------------
    try:
        graph_json = OUTPUT_DIR / "graph_full.json"
        graph_html = OUTPUT_DIR / "graph_interativo.html"

        graph_data = {
            "nodes": [{"id": n, "label": n} for n in graph.get_nodes()],
            "edges": [
                {"from": u, "to": v, "weight": attrs.get("weight", 1)}
                for u in graph.get_nodes()
                for v, attrs in graph.adj[u].items()
            ],
        }

        with open(graph_json, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Arquivo JSON salvo em: {graph_json}")

        viz_mod = import_module("viz")
        # se a função inline existir, usa ela (abre sem servidor). Caso contrário usa a existente.
        if hasattr(viz_mod, "generate_interactive_html_inline"):
            viz_mod.generate_interactive_html_inline(graph_html, graph_data)
            print(f"✅ HTML interativo (inline) gerado em: {graph_html}")
        elif hasattr(viz_mod, "generate_interactive_html"):
            viz_mod.generate_interactive_html(graph_html, str(graph_json.name))
            print(f"✅ HTML interativo gerado em: {graph_html}")
        elif hasattr(viz_mod, "gerar_visualizacao_interativa"):
            viz_mod.gerar_visualizacao_interativa(graph)
            print("✅ gerar_visualizacao_interativa() executada (fallback).")
        else:
            print("⚠️ Nenhuma função para gerar HTML interativo encontrada no viz.py")


    except Exception as e:
        print(f"🚨 Erro ao gerar HTML interativo: {e}", file=sys.stderr)
    # ------------------------------------------------------------------

    calculate_address_distances(graph)

    print("\n🎉 Todos os cálculos foram concluídos e salvos na pasta 'out/'.")

    from viz import (
        visualize_degree_heatmap,
        plot_density_ranking,
        visualize_top_degree_subgraph,
    )

    visualize_degree_heatmap(graph, OUTPUT_DIR / "grafo_heatmap.html")
    plot_density_ranking(
        output_filename=OUTPUT_DIR / "ranking_densidade.png",
        ego_csv_file=OUTPUT_DIR / "ego_bairro.csv",
        bairros_csv_file=BASE_DIR / "data" / "bairros_unique.csv",
    )
    visualize_top_degree_subgraph(graph, OUTPUT_DIR / "subgrafo_top10.html")

    output_html = OUTPUT_DIR / "microrregioes_interativo.html"
    output_json = OUTPUT_DIR / "microrregioes_graphs.json"
    visualize_microrregioes(graph, output_html, output_json)


if __name__ == "__main__":
    main()
