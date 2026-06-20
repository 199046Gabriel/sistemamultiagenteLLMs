# Estruturas de Dados e Algoritmos — Resumo Acadêmico

## 1. Recursão

Recursão é uma técnica em que uma função chama a si mesma para resolver subproblemas menores.
Todo algoritmo recursivo precisa de dois componentes:
- **Caso base**: condição de parada que evita recursão infinita.
- **Caso recursivo**: chamada à função com entrada reduzida.

### Exemplo: Fatorial
```
fatorial(n):
  se n == 0: retorna 1
  senão: retorna n * fatorial(n-1)
```

A pilha de chamadas armazena cada invocação até o caso base ser atingido.
A profundidade máxima depende do tamanho da entrada.

---

## 2. Árvores Binárias

Uma árvore binária é uma estrutura hierárquica onde cada nó tem no máximo dois filhos: esquerdo e direito.

### Terminologia:
- **Raiz**: nó sem pai.
- **Folha**: nó sem filhos.
- **Altura**: maior caminho da raiz até uma folha.
- **Nível**: distância de um nó até a raiz.

### Percursos:
- **Pré-ordem**: Raiz → Esquerda → Direita
- **Em-ordem**: Esquerda → Raiz → Direita (gera sequência ordenada em BST)
- **Pós-ordem**: Esquerda → Direita → Raiz

### Árvore Binária de Busca (BST):
Propriedade: filhos à esquerda são menores que a raiz; filhos à direita são maiores.
Busca, inserção e remoção têm complexidade O(log n) em árvores balanceadas.

---

## 3. Grafos

Um grafo G = (V, E) é composto por vértices V e arestas E.

### Tipos:
- **Direcionado (dígrafo)**: arestas têm direção.
- **Não-direcionado**: arestas são bidirecionais.
- **Ponderado**: arestas têm peso associado.

### Representações:
- **Matriz de adjacência**: O(V²) de espaço. Boa para grafos densos.
- **Lista de adjacência**: O(V + E) de espaço. Melhor para grafos esparsos.

### Algoritmos de Busca:
- **BFS (Busca em Largura)**: usa fila. Encontra o caminho mais curto em grafos não-ponderados.
- **DFS (Busca em Profundidade)**: usa pilha (ou recursão). Útil para detecção de ciclos e ordenação topológica.

---

## 4. Ordenação

### Bubble Sort — O(n²)
Compara pares adjacentes e troca os que estão fora de ordem. Simples mas ineficiente.

### Merge Sort — O(n log n)
Divide o array ao meio recursivamente, ordena cada metade e mescla.
Estável e eficiente. Usa memória auxiliar O(n).

### Quick Sort — O(n log n) médio / O(n²) pior caso
Escolhe um pivô, particiona o array em menores e maiores, e ordena recursivamente.
Na prática, é o mais rápido para arrays grandes.

### Heap Sort — O(n log n)
Usa uma estrutura de heap (max-heap ou min-heap) para ordenar.
Sem memória auxiliar extra (in-place).

---

## 5. Complexidade de Algoritmos (Notação Big O)

| Complexidade | Nome        | Exemplo                       |
|--------------|-------------|-------------------------------|
| O(1)         | Constante   | Acesso a array por índice     |
| O(log n)     | Logarítmica | Busca binária                 |
| O(n)         | Linear      | Busca sequencial              |
| O(n log n)   | Linearítmica| Merge Sort, Quick Sort        |
| O(n²)        | Quadrática  | Bubble Sort, Selection Sort   |
| O(2ⁿ)        | Exponencial | Subconjuntos, Torre de Hanói  |

---

## 6. Programação Dinâmica

Técnica que resolve problemas dividindo-os em subproblemas sobrepostos e armazenando os resultados intermediários (memoização ou tabulação).

### Quando usar:
- O problema tem subestrutura ótima.
- Os subproblemas se repetem.

### Exemplos clássicos:
- **Fibonacci** com memoização: O(n) ao invés de O(2ⁿ).
- **Problema da mochila (Knapsack)**: maximizar valor com peso limitado.
- **Maior subsequência comum (LCS)**.

---

## 7. Hashing

Uma tabela hash mapeia chaves a valores usando uma função hash.
- Acesso médio O(1) para inserção, remoção e busca.
- Colisões são tratadas por encadeamento (listas ligadas) ou endereçamento aberto.
- Fator de carga (α = n/m) afeta desempenho: quanto maior, mais colisões.
