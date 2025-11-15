import pytest
from src.graph import Graph
from src.algorithms import dijkstra

# --- Fixtures (Grafos de Teste) ---

@pytest.fixture
def graph_positivo():
    """Cria um grafo simples com pesos positivos para teste."""
    g = Graph()
    g.add_directed_edge("A", "B", weight=10)
    g.add_directed_edge("A", "C", weight=2)
    g.add_directed_edge("C", "B", weight=3) # Caminho A->C->B (custo 5)
    g.add_directed_edge("C", "D", weight=8)
    g.add_directed_edge("B", "D", weight=1) # Caminho A->C->B->D (custo 6)
    
    # Nó isolado
    g.add_node("E")
    return g

@pytest.fixture
def graph_negativo():
    """Cria um grafo com uma aresta de peso negativo."""
    g = Graph()
    g.add_directed_edge("A", "B", weight=5)
    g.add_directed_edge("A", "C", weight=2)
    g.add_directed_edge("C", "B", weight=-3) # Aresta negativa!
    return g

# --- Testes (Pesos Positivos) ---

def test_dijkstra_caminho_otimo(graph_positivo):
    """Testa se o Dijkstra encontra o caminho mais curto (A->C->B), não o mais direto (A->B)."""
    path, cost = dijkstra(graph_positivo, "A", "B")
    
    assert path == ["A", "C", "B"]
    assert cost == 5

def test_dijkstra_caminho_longo(graph_positivo):
    """Testa um caminho com múltiplas etapas (A->C->B->D)."""
    path, cost = dijkstra(graph_positivo, "A", "D")
    
    assert path == ["A", "C", "B", "D"]
    assert cost == 6

def test_dijkstra_sem_caminho(graph_positivo):
    """Testa um caminho para um nó isolado (E)."""
    path, cost = dijkstra(graph_positivo, "A", "E")
    
    assert path is None
    assert cost == float('inf')

def test_dijkstra_no_inexistente(graph_positivo):
    """Testa um caminho para um nó que não existe (Z)."""
    path, cost = dijkstra(graph_positivo, "A", "Z")
    
    assert path is None
    assert cost == float('inf')

# --- Teste (Peso Negativo) ---

def test_dijkstra_recusa_peso_negativo(graph_negativo):
    """
    Testa se o Dijkstra modificado levanta um erro ao encontrar um peso negativo.
    """
    # Verifica se a função 'dijkstra' levanta um 'ValueError'
    # com a mensagem "Peso negativo detectado"
    with pytest.raises(ValueError, match="Peso negativo detectado"):
        dijkstra(graph_negativo, "A", "B")