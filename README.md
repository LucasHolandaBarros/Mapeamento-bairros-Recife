# Mapeamento-bairros-Recife

## Introdução

Esse projeto é destinado para disciplina de Teoria de Grafos, onde está sendo manipulado dados de csvs e analisados em grafos. Alguns algoritmos como, Dijkstra, Bellman-Ford, DFS e BFS, foram analisados para percorrer caminhos mais curtos e baratos. Jsons foram gerados também com informações relacionadas aos tempos dos algoritmos, como é no caso da Segunda Parte. Outras informações como, peso, densidade, ordem e tamanho dos grafos também foram geradas em arquivos jsons.

# Parte 1

## Derretimento

Foi feito o derretimento do csv "bairros_recife.csv" para análise mais densa e específica dos dados, armazenamos essas informações em diferentes microrregiões e com seus respectivos bairros. O csv de destino foi o "bairros_unique", localizado na pasta /data.

## Grafo

O grafo dessa parte é um grafo interativo no qual o usuário pode escolher visualizar um caminho existente entre um determinado nó de destino e um nó de origem. Além disso, é possível visualizar especificações de cada bairro (vértice) disponível no csv, como: grau, nome e densidade

## Formas de Visualização:

Algumas formas de apresentação dos dados foram implementadas, como por exemplo:
  <ul>
    <li><strong>Grafo Interativo:</strong> Principal visualização, onde todos os bairros podem ser buscados e caminhos</li>
    <li><strong>Heatmap:</strong> Mapa de calor que mostra a cor depender da densidade de cada vértice</li>
    <li><strong>Divisão por microrregião:</strong> Grafo que mostra cada microrregião e seus respectivos bairros</li>
    <li><strong>Subgrafo top 10:</strong> Grafo que mostra um subgrafo com os dez grafos mais densos</li>
    <li><strong>Visualização de Caminhos:</strong> Grafo que mostra o caminho entre "Nova Descoberta" e "Setubal"</li>
  </ul>

## Arestas

As arestas foram classificadas a partir de alguns princípios:
<ul>
    <li><strong>Logradouro:</strong> Caminho mais rápido entre dois bairros, por exemplo: "Boa Viagem" e "Cabanga"</li>
    <li><strong>Observação:</strong> Descrição entre dois bairros, relacionada ao caminho específico, por exemplo: "2av + 1rua"</li>
    <li><strong>Pesos:</strong> Para cada tipo de via foi estabelecido um peso específico:
      <ul>
        <li><strong>Rua:</strong> peso 2</li>
        <li><strong>Avenida:</strong> peso 1</li>
        <li><strong>Pe ou Br:</strong> peso 0.5</li>
        <li><strong>Ponte ou Viaduto:</strong> peso 0.5</li>
      </ul>
    </li>
  </ul>

# Parte 2

## Descrição

O csv analisado foi sobre vôos com destino e partida no Brasil, o conjunto de vértices é formado por cidades/estados e o conjunto de arestas é formado por vôos. O grafo é direcionado e ponderado

## Algoritmos

Algoritmos como BFS, DFS, Dijkstra e Bellman-Ford

  <ul>
    <li><strong>BFS:</strong> informa-se a ordem, camadas e se há ocorrência de ciclos em três pontos de partida diferentes</li>
    <li><strong>DFS:</strong> informa-se a ordem, camadas e se há ocorrência de ciclos em três pontos de partida diferentes</li>
    <li><strong>Dijkstra:</strong> São analisados vértices com peso positivo, com 6 pares origem-destino</li>
    <li><strong>Bellman-Ford:</strong> Analisados dois casos um com peso negativo, porém sem ciclo negativo e o outro caso com ciclo negativo </li>
  </ul>

## Métricas

Tempo e memória por algoritmo/tarefa, arquivo salvo em um json. Saída do json

```bash
  {
    "Dijkstra": {
        "tempo": 0.002107399981468916,
        "memoria_MB": 0.02448272705078125
    },
    "BFS": {
        "tempo": 0.0024266999680548906,
        "memoria_MB": 0.01775360107421875
    },
    "DFS": {
        "tempo": 0.0008351000724360347,
        "memoria_MB": 0.020355224609375
    },
    "Bellman-Ford": {
        "tempo": 0.20019159989897162,
        "memoria_MB": 0.019256591796875
    }
}
```

## Visualização

<ul>
  <li>Visualização dos vôos internos que ocorreram no Brasil, em formato de grafo</li>
  <li>Visualização dos vôos internacionais com conexões diversas em diversos estados brasileiros</li>
</ul>
