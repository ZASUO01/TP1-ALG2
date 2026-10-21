# Trabalho Prático 1 – Indexação Geoespacial e Geometria Computacional Híbrida

Motor de busca geoespacial de entregadores em Belo Horizonte. Dado um ponto no mapa e um
raio, o sistema encontra todos os entregadores dentro do raio usando um índice
**Geohash + Trie compacta**, ambos implementados do zero, com filtro final pela distância
**haversine**. Os entregadores são sintéticos, gerados em torno dos bares da cidade e
projetados sobre a malha viária real (OpenStreetMap). A interface é feita em Dash +
dash-leaflet.

## Estrutura

```
app.py                  interface (Dash + dash-leaflet)
src/geohash.py          Geohash: encode, decode, center, neighbors
src/trie.py             Trie compacta (radix tree): insert, search por prefixo
src/search.py           haversine, escolha da precisão, índice e busca por raio
src/couriers.py         malha viária (osmnx) e geração dos entregadores
scripts/benchmark.py    comparação índice x força bruta
tests/                  testes (pytest)
data/bares.csv          bares de BH (dados abertos da PBH)
data/bares_geo.csv      mesmos bares com latitude/longitude (WGS84)
cache/                  malha viária baixada e cache do osmnx (não versionado)
```

## Como executar

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest                        # testes
.venv/bin/python app.py                 # interface em http://127.0.0.1:8050
.venv/bin/python -m scripts.benchmark   # experimentos
```

Na primeira execução da interface (ou do benchmark) a malha viária de BH é baixada do
OpenStreetMap (~1,5 min) e salva em `cache/bh_drive.graphml`; nas seguintes ela é lida do
disco (~3,5 s).

Uso da interface: escolha o número **N** de entregadores e clique em *Generate*; defina o
raio em km e clique em qualquer ponto do mapa. São exibidos o círculo de busca, as 9
células de geohash consultadas, os entregadores encontrados (em vermelho), a precisão
usada, o tempo da busca e os 10 entregadores mais próximos. A camada *Bars* (desligada por
padrão) mostra os 20.859 bares agrupados em clusters.

## Dados

`data/bares.csv` contém os estabelecimentos da PBH classificados como bares/restaurantes.
`data/bares_geo.csv` acrescenta as colunas `latitude` e `longitude` (WGS84), obtidas em
uma etapa de pré-processamento (geocodificação dos endereços) que não faz parte do código
deste repositório. <!-- TODO: descrever como a geocodificação foi feita -->

## Implementação

### Geohash (`src/geohash.py`)

- `encode(lat, lon, precision)`: a cada bit, o intervalo de uma coordenada é dividido ao
  meio e o bit indica em qual metade o ponto está. Os bits alternam entre longitude e
  latitude (começando pela longitude) e cada grupo de 5 bits vira um caractere da base 32
  `0123456789bcdefghjkmnpqrstuvwxyz`.
- `decode(geohash)`: refaz as divisões e devolve os intervalos `[lat_min, lat_max]` e
  `[lon_min, lon_max]` da célula; `center` devolve o centro.
- `neighbors(geohash)`: as 8 células adjacentes de mesma precisão, obtidas deslocando o
  centro da célula em uma altura/largura de célula em cada direção e codificando de novo
  (a longitude dá a volta em ±180°).

Pontos próximos tendem a compartilhar prefixo, mas não sempre: dois pontos a poucos
metros, em lados opostos da borda de uma célula, podem ter geohashes completamente
diferentes. Por isso a busca consulta também as vizinhas.

### Trie compacta (`src/trie.py`)

Árvore radix: cada aresta guarda uma string (`label`) em vez de um único caractere, e
nós com um só filho e sem valores não existem. Cada chave termina em um nó que guarda a
lista de valores daquela chave (vários entregadores podem ter o mesmo geohash).

- `insert(key, value)`: desce comparando a chave com o rótulo das arestas; se a chave
  diverge no meio de uma aresta, ela é dividida em um nó intermediário com a parte comum.
- `search(prefix)`: desce até consumir o prefixo (que pode terminar no meio de uma
  aresta) e coleta, com uma pilha, todos os valores da subárvore.

### Busca por raio (`src/search.py`)

1. Cada entregador é inserido na Trie com o geohash de precisão máxima (12); qualquer
   precisão menor vira uma busca por prefixo.
2. `precisionForRadius(r, lat)` escolhe a **maior** precisão cuja célula tem altura e
   largura ≥ r. A largura em km diminui com o cosseno da latitude; usa-se a latitude mais
   afastada do equador que o bloco pode alcançar, para não superestimá-la.
3. Consulta-se a Trie com a célula do ponto e suas 8 vizinhas e aplica-se o filtro
   haversine sobre os candidatos; o resultado é ordenado por distância.

**Correção:** o ponto de consulta está dentro da célula central, logo a distância dele até
a borda externa do bloco 3×3 é de pelo menos uma altura (ou largura) de célula, que é ≥ r.
Assim, todo ponto a distância ≤ r está em uma das 9 células, e o filtro haversine remove
os que estão no bloco mas fora do círculo. A busca devolve exatamente o mesmo conjunto da
força bruta (verificado nos testes e no benchmark). Se nem a precisão 1 basta (raios de
milhares de km), a busca percorre o índice inteiro.

### Entregadores sintéticos (`src/couriers.py`)

`generateCouriers(n, bars, graph, seed)` gera N entregadores (N escolhido na interface):
cada um sorteia um bar, recebe um ponto uniforme num disco de 500 m em torno dele e é
projetado no ponto mais próximo **sobre a geometria** da rua mais próxima da malha viária
(`network_type="drive"`, projetada em UTM para trabalhar em metros). Com `seed` o
resultado é reproduzível.

## Complexidade

Sejam `p` a precisão, `k = 12` o tamanho da chave, `N` o número de entregadores,
`c` o número de candidatos nas 9 células e `m` o número de resultados.

| Operação | Tempo |
|---|---|
| `encode` / `decode` | O(p) |
| `neighbors` | O(p) (8 codificações) |
| `insert` na Trie | O(k) (alfabeto de 32 símbolos, filhos em dicionário) |
| `search(prefixo)` | O(p + tamanho da subárvore) = O(p + c) |
| construção do índice | O(N·k) |
| busca por raio | O(p + c + m log m) |
| força bruta | O(N + m log m) |

Espaço da Trie: O(N) nós (numa árvore radix, no máximo ~2N nós para N chaves distintas).

## Testes

`pytest` executa 63 testes:

- **geohash**: valores de referência (`u4pruydqqvj`, `ezs42`, `s0000`), ida e volta
  (o ponto cai dentro da caixa de `decode(encode(p))`) e vizinhas (8, distintas, mesma
  precisão, formando exatamente a moldura 3×3 em torno da célula).
- **trie**: prefixos que terminam no meio de arestas, chave que é prefixo de outra, chaves
  repetidas, propriedade de compactação e comparação com `startswith` sobre 2.000
  geohashes aleatórios.
- **busca**: haversine, monotonicidade de `precisionForRadius`, comparação com força bruta
  (3.000 pontos, raios de 50 m a 10.000 km) e um caso com dois pontos a ~20 m em lados
  opostos da borda de uma célula.
- **entregadores**: quantidade N, todos sobre a rua e a ≤ 500 m do bar, reprodutibilidade
  com `seed` (grafo sintético, sem acesso à rede).

## Experimentos

`scripts/benchmark.py`: entregadores gerados sobre a malha real de BH; 100 consultas
centradas em bares sorteados; média por consulta. Ambos os métodos em Python puro, e
em todas as consultas o índice devolveu o mesmo conjunto da força bruta.

| N | raio (km) | precisão | candidatos | encontrados | índice (ms) | força bruta (ms) | ganho |
|---|---|---|---|---|---|---|---|
| 1.000 | 0,5 | 6 | 29 | 5 | 0,08 | 0,37 | 5× |
| 1.000 | 1 | 5 | 491 | 17 | 0,30 | 0,38 | 1× |
| 1.000 | 2 | 5 | 491 | 54 | 0,31 | 0,39 | 1× |
| 1.000 | 5 | 4 | 1.000 | 268 | 0,59 | 0,43 | <1× |
| 10.000 | 0,5 | 6 | 274 | 46 | 0,22 | 3,65 | 16× |
| 10.000 | 1 | 5 | 4.768 | 150 | 2,52 | 3,74 | 1,5× |
| 10.000 | 2 | 5 | 4.768 | 519 | 2,57 | 3,78 | 1,5× |
| 10.000 | 5 | 4 | 10.000 | 2.575 | 5,65 | 4,27 | <1× |
| 100.000 | 0,5 | 6 | 2.754 | 460 | 2,87 | 38,68 | 13× |
| 100.000 | 1 | 5 | 48.075 | 1.520 | 45,32 | 39,45 | <1× |
| 100.000 | 2 | 5 | 48.075 | 5.234 | 46,09 | 40,67 | <1× |
| 100.000 | 5 | 4 | 100.000 | 25.917 | 101,39 | 47,43 | <1× |

Construção do índice: 10 ms (N = 1.000), 99 ms (10.000), 1,35 s (100.000).

**Análise.** O ganho depende de quão bem o bloco 3×3 se ajusta ao círculo. Cada caractere
de geohash divide a célula por 32, então os tamanhos disponíveis são muito espaçados: em
BH a precisão 6 tem células de ~1,2 km × 0,6 km e a precisão 5 de ~4,9 km × 4,6 km.
Para r = 0,5 km a precisão 6 serve e o bloco 3×3 (~3,4 km × 1,8 km) contém só ~3% dos
entregadores, daí o ganho de 13–16×. Para r = 1 km ou 2 km a altura de 0,6 km já não
basta e a busca cai para a precisão 5, cujo bloco 3×3 (~15 km × 14 km) cobre quase metade
da cidade; para r = 5 km cai para a precisão 4 e cobre a cidade inteira. Nesses casos o
número de candidatos se aproxima de N e o índice fica no máximo empatado com a força
bruta, pois ainda paga o percurso da Trie. Além disso, os entregadores se concentram
perto dos bares (região central), o que aumenta os candidatos nas células centrais.

## Limitações e possíveis melhorias

- A escolha "célula + 8 vizinhas" exige células ≥ r, o que leva a blocos muito maiores
  que o círculo nos raios intermediários. Uma alternativa é usar uma precisão mais fina
  (célula ≈ r/2) e consultar todas as células que intersectam a caixa envolvente do
  círculo, ou permitir altura e largura de precisões diferentes.
- Perto dos polos as vizinhas norte/sul não existem (não ocorre em BH).
- A interface desenha cada entregador como um marcador; por isso N é limitado a 20.000.
- Clicar no painel de camadas do mapa também conta como clique de busca (comportamento
  do dash-leaflet).
