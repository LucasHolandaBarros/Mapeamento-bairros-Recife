import pytest
from src.graph import Graph
from src.algorithms import dijkstra

@pytest.fixture
def graph_positivo():

    g = Graph()
    g.add_directed_edge("A", "B", weight=10)
    g.add_directed_edge("A", "C", weight=2)
    g.add_directed_edge("C", "B", weight=3) 
    g.add_directed_edge("C", "D", weight=8)
    g.add_directed_edge("B", "D", weight=1) 
    
    g.add_node("E")
    return g

@pytest.fixture
def graph_negativo():
    
    g = Graph()
    g.add_directed_edge("A", "B", weight=5)
    g.add_directed_edge("A", "C", weight=2)
    g.add_directed_edge("C", "B", weight=-3) 
    return g

def test_dijkstra_caminho_otimo(graph_positivo):
    path, cost = dijkstra(graph_positivo, "A", "B")
    
    assert path == ["A", "C", "B"]
    assert cost == 5

def test_dijkstra_caminho_longo(graph_positivo):
    path, cost = dijkstra(graph_positivo, "A", "D")
    
    assert path == ["A", "C", "B", "D"]
    assert cost == 6

def test_dijkstra_sem_caminho(graph_positivo):
    path, cost = dijkstra(graph_positivo, "A", "E")
    
    assert path is None
    assert cost == float('inf')

def test_dijkstra_no_inexistente(graph_positivo):
    path, cost = dijkstra(graph_positivo, "A", "Z")
    
    assert path is None
    assert cost == float('inf')

def test_dijkstra_recusa_peso_negativo(graph_negativo):
    
    with pytest.raises(ValueError, match="Peso negativo detectado"):
        dijkstra(graph_negativo, "A", "B")