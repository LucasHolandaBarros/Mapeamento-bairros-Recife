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

    html = f"""
<html>
<head>
    <meta charset='utf-8'>
    <title>Grafos por País</title>
    <script src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>
    <style>
        body {{ margin:0; font-family: Arial, Helvetica, sans-serif; background: #f5f6fa; }}
        .top-bar {{ background: #007bff; color: white; padding: 15px; font-size: 22px; font-weight: bold; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin-bottom: 10px; }}
        .controls {{ width: 100%; text-align: center; padding: 10px 0; margin-bottom: 10px; }}
        select {{ padding: 10px; font-size: 16px; border-radius: 8px; border: 1px solid #ccc; margin-left: 10px; }}
        button {{ padding: 8px 12px; font-size:16px; margin-left:10px; border-radius:6px; border:1px solid #007bff; background:#007bff; color:white; cursor:pointer; }}
        #mynetwork {{ width: 100%; height: calc(100vh - 220px); background: white; border-radius: 10px; box-shadow: 0 3px 8px rgba(0,0,0,0.15); margin: 0 auto; }}
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

    <div class='controls'>
        <label>Origem:</label>
        <select id='originSelect'></select>
        <label>Destino:</label>
        <select id='destSelect'></select>
        <label>Algoritmo:</label>
        <select id='algorithmSelect'>
            <option value='dijkstra'>Dijkstra</option>
            <option value='bellmanford'>Bellman-Ford</option>
        </select>
        <button onclick='calcularCaminho()'>Calcular caminho</button>
    </div>

    <div id='mynetwork'></div>
    <div class='controls'><b id='result'></b></div>

<script>
const subgrafos = {json_safe};
let network, nodes, edges, currentData;

function atualizarGrafo() {{
    let pais = document.getElementById('paisSelect').value;
    if (!pais) return;

    let dados = subgrafos[pais];
    currentData = dados;

    nodes = new vis.DataSet(dados.nodes);
    edges = new vis.DataSet(
    dados.edges.map((e, i) => ({{
        id: i,
        from: e.from,
        to: e.to,
        title: 'Companhia: ' + e.companhia + '| Voo: ' + e.voo + '| Duração: ' + e.weight + 'h',
        realWeight: e.weight,  // adiciona peso real para cálculo
        value: 1.0 / e.weight
    }}))
);


    let container = document.getElementById('mynetwork');
    container.innerHTML = '';
    network = new vis.Network(container, {{ nodes, edges }}, {{
        nodes: {{ shape: 'dot', size: 12, color: {{ background: '#007bff', border: '#004aad' }}, font: {{ color: '#333', size: 18 }} }},
        edges: {{ color: '#ccc', arrows: 'to' }},
        physics: {{ enabled: true, solver: 'forceAtlas2Based', forceAtlas2Based: {{ springLength: 150, springConstant: 0.02, gravitationalConstant: -80 }}, maxVelocity: 30, minVelocity: 0.2, timestep: 0.15 }}
    }});

    let originSel = document.getElementById('originSelect');
    let destSel = document.getElementById('destSelect');
    originSel.innerHTML = ''; destSel.innerHTML = '';
    nodes.forEach(n => {{
        originSel.add(new Option(n.label, n.id));
        destSel.add(new Option(n.label, n.id));
    }});

    document.getElementById('result').textContent = '';
}}

// Dijkstra direcionado
function dijkstra(start, end) {{
    let dist = {{}}, prev = {{}};
    let nodeIds = nodes.getIds();
    nodeIds.forEach(n => {{ dist[n] = Infinity; prev[n] = null; }});
    dist[start] = 0;
    let unvisited = new Set(nodeIds);

    while (unvisited.size > 0) {{
        let u = Array.from(unvisited).reduce((a, b) => dist[a] < dist[b] ? a : b);
        unvisited.delete(u);

        edges.forEach(e => {{
            if (e.from === u) {{ // só direção correta
                let neighbor = e.to;
                let w = e.realWeight; // peso real em horas;
                if (dist[u] + w < dist[neighbor]) {{
                    dist[neighbor] = dist[u] + w;
                    prev[neighbor] = u;
                }}
            }}
        }});
    }}

    let path = [];
    let cur = end;
    if(dist[end] !== Infinity){{
        while(cur !== null){{
            path.unshift(cur);
            cur = prev[cur];
        }}
    }}

    return {{ cost: dist[end], path }};
}}

// Bellman-Ford direcionado
function bellmanFord(start, end) {{
    let dist = {{}}, prev = {{}};
    let nodeIds = nodes.getIds();
    nodeIds.forEach(n => {{ dist[n] = Infinity; prev[n] = null; }});
    dist[start] = 0;

    for (let i = 0; i < nodeIds.length - 1; i++) {{
        edges.forEach(e => {{
            let u = e.from, v = e.to, w = e.realWeight;
            if (dist[u] + w < dist[v]) {{
                dist[v] = dist[u] + w;
                prev[v] = u;
            }}
        }});
    }}

    let path = [];
    let cur = end;
    if(dist[end] !== Infinity){{
        while(cur !== null){{
            path.unshift(cur);
            cur = prev[cur];
        }}
    }}

    return {{ cost: dist[end], path }};
}}

function calcularCaminho() {{
    let start = document.getElementById('originSelect').value;
    let end = document.getElementById('destSelect').value;
    let algo = document.getElementById('algorithmSelect').value;

    if (!start || !end) return alert('Selecione origem e destino.');

    let res = (algo === 'dijkstra') ? dijkstra(start, end) : bellmanFord(start, end);

    // Reset cores
    nodes.forEach(n => nodes.update({{ id: n.id, color: '#007bff', size: 12 }}));
    edges.forEach(e => edges.update({{ id: e.id, color: '#ccc', width: 1 }}));

    let resultField = document.getElementById('result');

    if (!res.path.length) {{
        // Não há caminho
        resultField.textContent = 'Caminho: Não encontrado | Custo: —';
        return;
    }}

    // Destacar caminho
    for (let i = 0; i < res.path.length; i++) {{
        nodes.update({{ id: res.path[i], color: '#ff3b3b', size: 16 }});
        if (i < res.path.length - 1) {{
            edges.forEach(e => {{
                if (e.from === res.path[i] && e.to === res.path[i + 1]) {{
                    edges.update({{ id: e.id, color: '#ff3b3b', width: 3 }});
                }}
            }});
        }}
    }}

    resultField.textContent = 'Caminho: ' + res.path.join(' → ') + ' | Custo: ' + res.cost.toFixed(2) + 'h';
}}
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
