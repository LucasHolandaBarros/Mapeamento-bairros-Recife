import pytest
from src.graph import Graph
from src.algorithms import bfs


def test_bfs_sem_ciclo():
  
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")

    resultado = bfs(g, "A")

    assert resultado["ordem"] == 3
    assert resultado["camadas"] == 3    
    assert resultado["ha_ciclos"] is False


def test_bfs_ciclo_simples():
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "A")

    resultado = bfs(g, "A")

    assert resultado["ha_ciclos"] is True
    assert resultado["ordem"] == 3
    assert resultado["camadas"] == 3


def test_bfs_desconexo():
   
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_node("C")

    resultado = bfs(g, "A")

    assert resultado["ordem"] == 2
    assert resultado["camadas"] == 2  
    assert resultado["ha_ciclos"] is False


def test_bfs_ciclo_multiplo():
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "A")  

    g.add_directed_edge("B", "D")
    g.add_directed_edge("D", "B")  

    resultado = bfs(g, "A")

    assert resultado["ha_ciclos"] is True
    assert resultado["ordem"] == 4


def test_bfs_niveis_corretos_grafo_pequeno():
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("A", "C")
    g.add_directed_edge("B", "D")

    resultado = bfs(g, "A")

    assert resultado["camadas"] == 3
    assert resultado["ha_ciclos"] is False
    assert resultado["ordem"] == 4
