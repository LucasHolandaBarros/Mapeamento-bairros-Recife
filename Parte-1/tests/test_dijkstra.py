import pytest
import sys
from pathlib import Path

# Adiciona o diretório 'src' ao path para que possamos importar 'Graph' e 'dijkstra'
# Isso é necessário para rodar o 'pytest' da raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

# Agora podemos importar nossos módulos
from graphs.graph import Graph
from graphs.algorithms import dijkstra

@pytest.fixture
def grafo_teste_simples():
    # Criando um grfo de testes 
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_node("E")
    
    g.add_edge("A", "B", weight=2)
    g.add_edge("A", "C", weight=5)
    g.add_edge("B", "C", weight=1)
    g.add_edge("B", "D", weight=6)
    g.add_edge("C", "D", weight=3)
    
    return g

# --- Nossos Casos de Teste ---

def test_caminho_mais_barato(grafo_teste_simples):

    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "C")
    
    assert custo == 3
    assert caminho == ["A", "B", "C"]

def test_caminho_complexo(grafo_teste_simples):

    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "D")
    
    assert custo == 6
    assert caminho == ["A", "B", "C", "D"]

def test_sem_caminho(grafo_teste_simples):
    
    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "E")
    
    assert custo == float('inf')
    assert caminho == []

def test_no_origem_igual_destino(grafo_teste_simples):
    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "A")
    
    assert custo == 0
    assert caminho == ["A"]

def test_no_inexistente(grafo_teste_simples):
    g = grafo_teste_simples

    caminho, custo = dijkstra(g, "A", "Z")
    
    assert caminho is None
    assert custo == float('inf')
   