import pytest
import math
from src.graph import Graph  # Importa a classe Graph da pasta src
from src.algorithms import bellman_ford # Importa a função a ser testada

# --- Fixtures (Grafos de Teste) ---

@pytest.fixture
def graph_negativo_sem_ciclo():
    """
    (i) Grafo com pesos negativos, mas SEM ciclo negativo.
    
    Caminhos de "S":
    S -> A: 5
    S -> B: 10
    S -> A -> B: 5 + (-3) = 2  <- Este é o caminho mais curto para B
    """
    g = Graph()
    g.add_directed_edge("S", "A", weight=5)
    g.add_directed_edge("S", "B", weight=10)
    g.add_directed_edge("A", "B", weight=-3) # Aresta negativa
    g.add_node("C") # Nó inalcançável
    return g

@pytest.fixture
def graph_com_ciclo_negativo():
    """
    (ii) Grafo COM um ciclo negativo.
    
    Ciclo: A -> B -> C -> A
    Custo: 2 + 3 + (-6) = -1
    """
    g = Graph()
    g.add_directed_edge("A", "B", weight=2)
    g.add_directed_edge("B", "C", weight=3)
    g.add_directed_edge("C", "A", weight=-6) # Aresta que cria o ciclo negativo
    return g

# --- Testes ---

def test_bellman_ford_distancias_corretas(graph_negativo_sem_ciclo):
    """
    Testa (i): Pesos negativos sem ciclo.
    Verifica se as distâncias estão corretas.
    """
    fonte = "S"
    resultado = bellman_ford(graph_negativo_sem_ciclo, fonte)
    
    distancias = resultado["distancias"]
    
    # Distâncias esperadas
    distancias_esperadas = {
        "S": 0,
        "A": 5,                # Caminho: S -> A
        "B": 2,                # Caminho: S -> A -> B (custo 5 + (-3) = 2)
        "C": float('inf')      # Nó inalcançável
    }
    
    # Verificação
    assert not resultado["ha_ciclo_negativo"]
    
    # Compara valores, tratando 'inf'
    for no, dist in distancias_esperadas.items():
        assert math.isinf(distancias[no]) == math.isinf(dist)
        if not math.isinf(dist):
            assert distancias[no] == dist

def test_bellman_ford_detecta_ciclo_negativo(graph_com_ciclo_negativo):
    """
    Testa (ii): Com ciclo negativo.
    Verifica se a 'flag' é True.
    """
    fonte = "A"
    resultado = bellman_ford(graph_com_ciclo_negativo, fonte)
    
    # A única coisa que importa é a detecção do ciclo.
    # As distâncias são indefinidas (podem ser -inf)
    assert resultado["ha_ciclo_negativo"]