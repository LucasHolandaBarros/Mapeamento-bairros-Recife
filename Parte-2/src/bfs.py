def bfs(self, fonte):
    visitado = {}
    camada = {}
    ordem = []
    fila = []
    ciclos = False

    # Inicializa a única fonte
    visitado[fonte] = True
    camada[fonte] = 0
    fila.append(fonte)

    # BFS
    while fila:
        u = fila.pop(0)
        ordem.append(u)

        for viz in self.adj.get(u, []):
            if viz not in visitado:
                visitado[viz] = True
                camada[viz] = camada[u] + 1
                fila.append(viz)
            else:
                if viz not in fila and camada[viz] <= camada[u]:
                    ciclos = True

    # resumo
    countOrdem = len(ordem)
    countCamadas = max(camada.values()) + 1 if camada else 0

    return {
        "ordem": countOrdem,
        "camadas": countCamadas,
        "ha_ciclos": ciclos,
    }



