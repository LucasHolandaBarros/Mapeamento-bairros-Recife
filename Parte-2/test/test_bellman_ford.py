import pytest
import math
from src.graph import Graph  
from src.algorithms import bellman_ford 

@pytest.fixture
def graph_negativo_sem_ciclo():
   
    g = Graph()
    g.add_directed_edge("S", "A", weight=5)
    g.add_directed_edge("S", "B", weight=10)
    g.add_directed_edge("A", "B", weight=-3) 
    g.add_node("C") 
    return g

@pytest.fixture
def graph_com_ciclo_negativo():
    
    g = Graph()
    g.add_directed_edge("A", "B", weight=2)
    g.add_directed_edge("B", "C", weight=3)
    g.add_directed_edge("C", "A", weight=-6) 
    return g

# --- Testes ---

def test_bellman_ford_distancias_corretas(graph_negativo_sem_ciclo):
    
    fonte = "S"
    resultado = bellman_ford(graph_negativo_sem_ciclo, fonte)
    
    distancias = resultado["distancias"]
    
    distancias_esperadas = {
        "S": 0,
        "A": 5,                
        "B": 2,                
        "C": float('inf')      
    }
    
    assert not resultado["ha_ciclo_negativo"]
    
    for no, dist in distancias_esperadas.items():
        assert math.isinf(distancias[no]) == math.isinf(dist)
        if not math.isinf(dist):
            assert distancias[no] == dist

def test_bellman_ford_detecta_ciclo_negativo(graph_com_ciclo_negativo):
    
    fonte = "A"
    resultado = bellman_ford(graph_com_ciclo_negativo, fonte)
    
    assert resultado["ha_ciclo_negativo"]