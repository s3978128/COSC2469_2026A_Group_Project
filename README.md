# Smart Path Finder Program

Smart Path Finder is a Python routing project over directed road graphs where:

- nodes are locations/intersections
- edges are roads with
  - fixed distance
  - 24 hourly travel-time values (`time_0..time_23`)

The code uses only built-in Python data types and standard-library modules.

## Core Features

- Distance-optimized route search
- Time-optimized route search (hour-dependent edge costs)
- Optional constraints for each query:
  - avoid nodes
  - avoid directed edges
- Per-route reporting includes:
  - node sequence
  - total distance
  - total travel time
- Dataset generation and persistence (`nodes.csv`, `edges.csv`, `metadata.json`)
- Benchmark pipeline for stored datasets

## Project Layout

- `src/main.py`: interactive CLI
- `src/algorithms/dijkstra.py`: generic Dijkstra with optional constraints
- `src/cost/distance_cost.py`: distance objective
- `src/cost/time_cost.py`: time objective
- `src/graph/`: graph, node, edge models
- `src/generator/graph_generator.py`: realistic graph generation
- `src/generator/generate_datasets.py`: persistent dataset generation
- `src/dataio/graph_io.py`: CSV/JSON import-export
- `src/evaluation/benchmark.py`: benchmark utilities
- `src/evaluation/benchmark_datasets.py`: benchmark runner for stored datasets
- `src/utils/visualization.py`: network/path rendering
- `tests/`: unit tests

## Quick Start

1. Create and activate a virtual environment.
2. Run tests.
3. Generate datasets.
4. Benchmark datasets.
5. Explore interactively with CLI.

From project root:

```bash
python -m unittest discover -s tests -v
python src/generator/generate_datasets.py
python src/evaluation/benchmark_datasets.py
python src/main.py
```

## Practical CLI Workflow

Run:

```bash
python src/main.py
```

Recommended flow:

1. Select network
2. Use option `1` to inspect graph and node IDs
3. Use option `2` (distance) or `3` (time)
4. Provide optional constraints when prompted:
  - avoid nodes: `N_1_2,N_3_4`
  - avoid edges: `N_1_2->N_1_3,N_3_4->N_3_5`
5. Review output:
  - path sequence
  - total distance
  - total travel time
  - segment breakdown

Visualization legend includes:

- `S` start node
- `E` end node
- `●` shortest-path nodes
- `◍` visited nodes

## Graph Generation and Storage

### Generate datasets

```bash
python src/generator/generate_datasets.py
```

Default generated sets:

- `graph_100` (10x10)
- `graph_1000` (25x40)
- `graph_5000` (50x100)

Each dataset folder contains:

- `nodes.csv`
- `edges.csv`
- `metadata.json`

### File format

- `nodes.csv`: `node_id,x,y`
- `edges.csv`: `source,destination,distance,time_0..time_23`
- `metadata.json`: dataset summary + generation parameters

### Import/export APIs

- `export_graph_csv(graph, output_dir, metadata=None)`
- `import_graph_csv(input_dir)`

Implemented in `src/dataio/graph_io.py`.

## Benchmark Pipeline

Run:

```bash
python src/evaluation/benchmark_datasets.py
```

Outputs:

- `results/runtime_results.csv`
- `results/analysis.txt`

Benchmark CSV now also includes explainability/search-effort metrics when
available (for example expanded node counts) so runtime numbers can be
interpreted with search behavior.

Benchmark runner evaluates each registered algorithm for both objectives:

- distance (`cost_by_distance`)
- time (`cost_by_time`)

## Bidirectional Search

### Motivation

Single-source Dijkstra expands outward from the start only. Bidirectional
Dijkstra runs two searches simultaneously:

- forward from source
- backward from destination

On many graphs this reduces the explored region and can improve runtime.

### Implementation Approach

The project implementation is in `src/algorithms/bidirectional_dijkstra.py` and
uses:

1. Two priority queues (`forward`, `backward`)
2. Two distance maps (`dist_f`, `dist_b`)
3. Two predecessor maps for path reconstruction (`prev_f`, `next_b`)
4. Stopping rule based on current best meeting cost

The graph model provides cached incoming-edge access via reverse adjacency to
avoid rebuilding reverse structure for every query.

### Overhead Issue and Fix

Initial bidirectional runs were slower than expected on larger datasets because
the algorithm repeatedly rebuilt incoming-edge lookup data per query. That
preprocessing overhead was paid many times during benchmarking and reduced the
runtime advantage of two-sided search.

The fix was to move reverse-neighbor construction into the graph model as a
cache that is reused across queries:

- `Graph.reverse_neighbors(node_id)` now reads from `_reverse_adj_cache`
- cache is built once lazily and reused
- cache is invalidated only when graph structure changes (for example `add_edge`)

Result: bidirectional search keeps its algorithmic benefit (fewer expanded
nodes on many queries) without paying repeated reverse-graph setup costs.

### Constraint Handling

Bidirectional search respects the same optional constraints as Dijkstra:

- avoided nodes are never expanded
- avoided directed edges are skipped in both forward and backward steps

### Explainability Metrics

The algorithm reports search-effort statistics (when `return_stats=True`):

- `expanded_forward`
- `expanded_backward`
- `expanded_nodes` (sum)

These are propagated to benchmark CSV summaries as min/mean/max so reported
runtime can be explained by how much of the graph was actually explored.

### Practical Interpretation

If bidirectional search is faster on a dataset, check whether expanded-node
metrics are also lower. If runtime does not improve, common causes include:

- directed topology limiting early meeting
- algorithm overhead dominating on very small graphs
- query pairs that do not benefit from two-sided expansion

## A* and Quality Metrics

### A* (A-star) in this project context

A* is a best-first shortest-path method that prioritizes nodes using:

$$
f(n) = g(n) + h(n)
$$

where:

- $g(n)$ is the exact cost from start to node $n$
- $h(n)$ is a heuristic estimate from $n$ to goal

For grid-like road graphs with distance objective, a common heuristic is
Euclidean distance between node coordinates. If $h(n)$ never overestimates true
remaining cost (admissible), A* returns an optimal path while usually expanding
fewer nodes than Dijkstra.

Practical notes:

- if $h(n)=0$, A* behaves like Dijkstra
- better heuristics reduce expansions and runtime
- for time-dependent costs, heuristic design is harder because edge travel time
  changes by hour

### Optimality Gap

Optimality gap measures how far an algorithm's route cost is from a reference
optimal cost (typically Dijkstra for the same objective and constraints):

$$
\mathrm{gap}(\%) = \frac{C_{alg} - C_{opt}}{C_{opt}} \times 100
$$

Interpretation:

- `0%` means optimal
- positive values mean worse-than-optimal cost
- useful for approximate or bounded-suboptimal methods

### Stress (for search effort/load)

Stress is a workload indicator showing how hard a query was for an algorithm.
A simple and useful stress metric is expansion ratio:

$$
\mathrm{stress} = \frac{\mathrm{expanded\_nodes}}{|V|}
$$

where $|V|$ is total graph nodes. You can also report raw `expanded_nodes`.

Interpretation:

- lower stress usually means less search effort
- compare stress with runtime to explain why one algorithm is faster or slower
- high stress with low optimality gap indicates correctness but heavier search

These two metrics complement runtime:

- runtime tells speed
- optimality gap tells solution quality
- stress tells search workload

## Add a New Algorithm

Use this checklist.

1. Create algorithm file in `src/algorithms/`.
2. Ensure the function signature is compatible with benchmark calls:

```python
def my_algo(graph, start, goal, cost_func, start_time=0, **kwargs):
   # return at least (path, total_cost)
   return path, total_cost
```

3. Register it in `ALGORITHM_REGISTRY` in `src/evaluation/benchmark_datasets.py`.
4. Add unit tests in `tests/`:
  - path correctness
  - unreachable behavior
  - optional avoid constraints
5. Re-run pipeline:

```bash
python -m unittest discover -s tests -v
python src/evaluation/benchmark_datasets.py
```

## Review an Algorithm Before Benchmarking

Use this practical review checklist.

1. Correctness:
  - returns valid node sequence
  - matches expected objective cost
2. Constraints:
  - avoid nodes respected
  - avoid directed edges respected
3. Robustness:
  - handles missing/unreachable nodes cleanly
  - no negative-cost assumptions violated
4. Compatibility:
  - works with both `cost_by_distance` and `cost_by_time`
  - returns at least `(path, total_cost)`

## Notes

- Graph is directed; visual proximity does not imply direct reachability.
- Time objective uses rolling hour based on cumulative minutes.
- Edge/node ratios for generated datasets are in realistic ranges for this project scale.