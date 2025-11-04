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
    """
    Cria um "grafo de brinquedo" previsível para todos os testes.
    
    A -> B (2)
    A -> C (5)
    B -> C (1)
    B -> D (6)
    C -> D (3)
    E (isolado)
    """
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
    """
    Testa se Dijkstra encontra o caminho mais barato,
    mesmo que não seja o mais curto em "saltos".
    
    Caminho A -> C (custo 5)
    Caminho A -> B -> C (custo 2 + 1 = 3) <- CORRETO
    """
    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "C")
    
    assert custo == 3
    assert caminho == ["A", "B", "C"]

def test_caminho_complexo(grafo_teste_simples):
    """
    Testa um caminho que envolve múltiplas etapas.
    A -> B -> C -> D (custo 2 + 1 + 3 = 6) <- CORRETO
    A -> C -> D (custo 5 + 3 = 8)
    A -> B -> D (custo 2 + 6 = 8)
    """
    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "D")
    
    assert custo == 6
    assert caminho == ["A", "B", "C", "D"]

def test_sem_caminho(grafo_teste_simples):
    """Testa um caminho para um nó isolado."""
    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "E")
    
    assert custo == float('inf')
    assert caminho == []

def test_no_origem_igual_destino(grafo_teste_simples):
    """Testa o caminho de um nó para ele mesmo."""
    g = grafo_teste_simples
    custo, caminho = dijkstra(g, "A", "A")
    
    assert custo == 0
    assert caminho == ["A"]

def test_no_inexistente(grafo_teste_simples):
    """Testa o que acontece se um nó não existir."""
    g = grafo_teste_simples
    
    custo_origem_fake, caminho_origem_fake = dijkstra(g, "Z", "A")
    assert custo_origem_fake == float('inf')
    assert caminho_origem_fake == []
    
    custo_destino_fake, caminho_destino_fake = dijkstra(g, "A", "Z")
    assert custo_destino_fake == float('inf')
    assert caminho_destino_fake == []