# Smart Path Finder

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

Benchmark runner evaluates each registered algorithm for both objectives:

- distance (`cost_by_distance`)
- time (`cost_by_time`)

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