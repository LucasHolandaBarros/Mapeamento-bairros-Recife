import pytest
from src.graph import Graph
from src.algorithms import bfs


def test_bfs_sem_ciclo():
    """
    Grafo simples em linha: A -> B -> C
    Não possui ciclos.
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")

    resultado = bfs(g, "A")

    assert resultado["ordem"] == 3
    assert resultado["camadas"] == 3    # A (0), B (1), C (2)
    assert resultado["ha_ciclos"] is False


def test_bfs_ciclo_simples():
    """
    Grafo com ciclo: A -> B -> C -> A
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "A")

    resultado = bfs(g, "A")

    assert resultado["ha_ciclos"] is True
    assert resultado["ordem"] == 3
    assert resultado["camadas"] == 3

"""
def test_bfs_camada_correta():
    
    Grafo onde BFS deve gerar camadas:
        A
       / \
      B   C
         /
        D
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("A", "C")
    g.add_directed_edge("C", "D")

    resultado = bfs(g, "A")

    assert resultado["camadas"] == 3  # A=0, B=1, C=1, D=2
    assert resultado["ha_ciclos"] is False
"""

def test_bfs_desconexo():
    """
    Grafo com componente separado:
    A -> B,   C isolado
    BFS(A) não visita C.
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_node("C")

    resultado = bfs(g, "A")

    assert resultado["ordem"] == 2
    assert resultado["camadas"] == 2  # A=0, B=1
    assert resultado["ha_ciclos"] is False


def test_bfs_ciclo_multiplo():
    """
    Grafo com ciclos múltiplos:
    A -> B, B -> C, C -> A e B -> D -> B
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "A")  # ciclo 1

    g.add_directed_edge("B", "D")
    g.add_directed_edge("D", "B")  # ciclo 2

    resultado = bfs(g, "A")

    assert resultado["ha_ciclos"] is True
    assert resultado["ordem"] == 4


def test_bfs_niveis_corretos_grafo_pequeno():
    """
    Verifica se o BFS calcula corretamente as camadas (níveis) em um grafo pequeno:

        A
       / \
      B   C
     /
    D

    Camadas:
    A=0, B=1, C=1, D=2  => total = 3 camadas
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("A", "C")
    g.add_directed_edge("B", "D")

    resultado = bfs(g, "A")

    # BFS retorna:
    # "camadas": max(camada.values()) + 1
    assert resultado["camadas"] == 3
    assert resultado["ha_ciclos"] is False
    assert resultado["ordem"] == 4
