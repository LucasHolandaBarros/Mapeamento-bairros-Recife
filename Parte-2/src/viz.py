import os
import json
from .graph import Graph

def visualize_ego_network(full_graph: Graph, filename="Relation_Voos.html"):
    print("\n[DEBUG] Iniciando geração do HTML...")

    brasil_nodes = []
    mundo_nodes = []

    for node, attrs in full_graph.nodes.items():
        pais = attrs.get("Pais")
        if pais == "Brasil":
            brasil_nodes.append(node)
        else:
            mundo_nodes.append(node)

    print(f"[DEBUG] Nós do Brasil: {len(brasil_nodes)}")
    print(f"[DEBUG] Nós do resto do mundo: {len(mundo_nodes)}")


    sub_brasil = {"nodes": [], "edges": []}
    brasil_set = set(brasil_nodes)

    for u in brasil_nodes:
        sub_brasil["nodes"].append({"id": u, "label": u})

    for u in brasil_set:
        if u not in full_graph.adj:
            continue
        for v, attrs in full_graph.adj[u].items():
            if v in brasil_set:
                sub_brasil["edges"].append({
                    "from": u,
                    "to": v,
                    "weight": float(attrs.get("weight", 1.0)),
                    "companhia": str(attrs.get("companhia", "")),
                    "voo": str(attrs.get("voo", ""))
                })

    print(f"[DEBUG] Arestas Brasil: {len(sub_brasil['edges'])}")

    sub_mundo = {"nodes": [], "edges": []}
    usados = set()

    for u in brasil_nodes:
        if u not in full_graph.adj:
            continue
        for v, attrs in full_graph.adj[u].items():
            if v in mundo_nodes:
                usados.add(u)
                usados.add(v)
                sub_mundo["edges"].append({
                    "from": u,
                    "to": v,
                    "weight": float(attrs.get("weight", 1.0)),
                    "companhia": str(attrs.get("companhia", "")),
                    "voo": str(attrs.get("voo", ""))
                })

    for n in usados:
        sub_mundo["nodes"].append({"id": n, "label": n})

    print(f"[DEBUG] Arestas Mundo: {len(sub_mundo['edges'])}")

    subgrafos = {
        "Brasil": sub_brasil,
        "Resto do Mundo": sub_mundo
    }

    json_safe = json.dumps(subgrafos).replace("</", "<\\/")

    
    os.makedirs("out", exist_ok=True)
    filepath = os.path.join("out", filename)


    html = """
<html>
<head>
    <meta charset='utf-8'>
    <title>Grafos por País</title>

    <script src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>

    <style>
        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #f5f6fa;
        }
        .top-bar {
            background: #007bff;
            color: white;
            padding: 15px;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 10px;
        }
        .controls {
            width: 100%;
            text-align: center;
            padding: 10px 0;
            margin-bottom: 10px;
        }
        select {
            padding: 10px;
            font-size: 16px;
            border-radius: 8px;
            border: 1px solid #ccc;
            margin-left: 10px;
        }
        #mynetwork {
            width: 100%;
            height: calc(100vh - 150px);
            background: white;
            border-radius: 10px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.15);
            margin: 0 auto;
        }
    </style>
</head>

<body>

    <div class='top-bar'>Mapa Interativo de Voos</div>

    <div class='controls'>
        <label style='font-size:18px;font-weight:bold;'>Selecionar grupo:</label>
        <select id='paisSelect' onchange='atualizarGrafo()'>
            <option value=''>Selecione...</option>
            <option value='Brasil'>Brasil (voos internos)</option>
            <option value='Resto do Mundo'>Resto do Mundo (Brasil → Exterior)</option>
        </select>
    </div>

    <div id='mynetwork'></div>

<script>

    const subgrafos = """ + json_safe + """;

    function atualizarGrafo() {

        let pais = document.getElementById('paisSelect').value;
        if (!pais) return;

        let dados = subgrafos[pais];

        let nodes = new vis.DataSet(dados.nodes);

        let edges = new vis.DataSet(
            dados.edges.map(function(e, index) {
                return {
                    id: index,
                    from: e.from,
                    to: e.to,
                    title: 'Companhia: ' + e.companhia + '<br>Voo: ' + e.voo + '<br>Duração: ' + e.weight + 'h',
                    value: 1.0 / e.weight
                };
            })
        );

        var options = {
            nodes: {
                shape: 'dot',
                size: 12,
                color: { background: '#007bff', border: '#004aad' },
                font: { color: '#333', size: 18 }
            },
            edges: {
                color: '#ccc',
                arrows: 'to'
            },
            physics: {
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    springLength: 150,
                    springConstant: 0.02,
                    gravitationalConstant: -80
                },
                maxVelocity: 30,
                minVelocity: 0.2,
                timestep: 0.15
            }
        };

        var container = document.getElementById('mynetwork');
        container.innerHTML = '';

        var network = new vis.Network(container, { nodes: nodes, edges: edges }, options);

        // -----------------------------------------------------------
        // ⭐ DESTACAR CONEXÕES AO CLICAR NO NÓ
        // -----------------------------------------------------------
        network.on("click", function (params) {

    // Se nada foi clicado → reset
    if (!params.nodes.length) {
        nodes.forEach(n => nodes.update({ id: n.id, color: "#007bff" }));
        edges.forEach(e => edges.update({ id: e.id, color: "#ccc", width: 1 }));
        return;
    }

    let selected = params.nodes[0];

    // Reset rápido
    nodes.forEach(n => nodes.update({ id: n.id, color: "#007bff" }));
    edges.forEach(e => edges.update({ id: e.id, color: "#ccc", width: 1 }));

    // Nó clicado
    nodes.update({ id: selected, color: "#ff3b3b" });

    // Vizinhos e arestas conectadas (API nativa do Vis-Network)
    let vizinhos = network.getConnectedNodes(selected);
    let arestas = network.getConnectedEdges(selected);

    // Pinta vizinhos
    vizinhos.forEach(n => nodes.update({ id: n, color: "#00c853" }));

    // Pinta arestas
    arestas.forEach(e => edges.update({ id: e, color: "#ff3b3b", width: 3 }));
});
    }

</script>

</body>
</html>
"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] HTML gerado com sucesso: {filepath}\n")
    except Exception as e:
        print("[ERRO] Falha ao salvar o HTML:")
        print(e)
