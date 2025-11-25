import pytest
from src.graph import Graph
from src.algorithms import dfs


def test_dfs_sem_ciclo():
   
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is False
    assert resultado["ordem"] == 3
    assert resultado["camadas"] == 3  


def test_dfs_com_ciclo_simples():
    """
    Grafo com ciclo direto:
        A → B → C → A
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "A")  

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is True
    assert resultado["ordem"] == 3
    assert resultado["camadas"] >= 1


def test_dfs_com_ciclo_de_profunda():
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "D")
    g.add_directed_edge("D", "E")
    g.add_directed_edge("E", "C")  

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is True


def test_dfs_arestas_do_tipo_retorno():
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "D")
    g.add_directed_edge("D", "B")  

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is True


def test_dfs_desconexo_sem_ciclo():
    
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_node("C")  

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is False
    assert resultado["ordem"] == 2
    assert resultado["camadas"] == 2 
