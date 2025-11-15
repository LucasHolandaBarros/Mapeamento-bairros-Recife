import pytest
from src.graph import Graph
from src.algorithms import dfs


def test_dfs_sem_ciclo():
    """
    Grafo simples sem ciclos:
        A → B → C
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is False
    assert resultado["ordem"] == 3
    assert resultado["camadas"] == 3  # camadas: A=0, B=1, C=2


def test_dfs_com_ciclo_simples():
    """
    Grafo com ciclo direto:
        A → B → C → A
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "A")  # ciclo

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is True
    assert resultado["ordem"] == 3
    # número de camadas pode variar, mas deve ser positivo
    assert resultado["camadas"] >= 1


def test_dfs_com_ciclo_de_profunda():
    """
    Ciclo "profundo":
        A → B → C
              ↑   ↓
              E ← D
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "D")
    g.add_directed_edge("D", "E")
    g.add_directed_edge("E", "C")  # ciclo profundo

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is True


def test_dfs_arestas_do_tipo_retorno():
    """
    Testa se o DFS detecta arestas de retorno (back edges).
    O log indica ciclo quando encontra um nó já visitado
    cuja camada é <= profundidade atual.
    
        A → B → C
             ↑
             └── D
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_directed_edge("B", "C")
    g.add_directed_edge("C", "D")
    g.add_directed_edge("D", "B")  # back edge → ciclo

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is True


def test_dfs_desconexo_sem_ciclo():
    """
    Grafo desconexo, porém sem ciclos:
        A → B
        C
    """
    g = Graph()
    g.add_directed_edge("A", "B")
    g.add_node("C")  # nó isolado

    resultado = dfs(g, "A")

    assert resultado["ha_ciclos"] is False
    assert resultado["ordem"] == 2
    assert resultado["camadas"] == 2  # A=0, B=1
