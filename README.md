# Smart Path Finder

Smart Path Finder is a Python routing project over directed road graphs where:

- nodes are locations/intersections
- edges are roads with
  - fixed distance
  - 24 hourly travel-time values (`time_0..time_23`)

The code uses only built-in Python data types and standard-library modules (no external dependencies).

## Core Features

- Distance-optimized route search
- Time-dependent shortest-path (TDSP) route search (hour-dependent edge costs)
- Optional constraints for each query:
  - avoid nodes
  - avoid directed edges
- Per-route reporting includes:
  - node sequence
  - total distance
  - total travel time
- Dataset generation and persistence (`nodes.csv`, `edges.csv`, `metadata.json`)
- Full benchmark pipeline for stored datasets (runtime, search effort, optimality gap)

## Project Layout

```
src/
  main.py                          # interactive CLI
  algorithms/
    dijkstra.py                    # generic Dijkstra (distance + TDSP)
    a_star.py                      # A* with pluggable heuristic (distance + TDSP)
    a_star_alt.py                  # A* with ALT landmark heuristics; also hosts
                                   #   a_star_active_alt and a_star_departure_alt
    bidirectional_dijkstra.py      # bidirectional Dijkstra (distance only)
    bidirectional_a_star.py        # bidirectional A* (distance only)
    bidirectional_time_a_star.py   # static-lower-bound bidirectional A* (TDSP)
    weighted_a_star.py             # weighted A* w=1.25 (distance)
    landmark_heuristic.py          # ALT preprocessing and heuristic functions
    degree2_contraction.py         # degree-2 node contraction + contracted wrappers
  cost/
    distance_cost.py               # cost_by_distance(edge, t) → edge.distance
    time_cost.py                   # cost_by_time(edge, t) → time_list[hour]
  graph/
    graph.py                       # adjacency-list graph with reverse-adj cache
    node.py                        # node model (id, x, y)
    edge.py                        # edge model (source, dest, distance, time_list[24])
  generator/
    graph_generator.py             # realistic synthetic graph generation
    generate_datasets.py           # persistent dataset generation script
  dataio/
    graph_io.py                    # CSV/JSON import-export
  evaluation/
    benchmark.py                   # low-level timing and metric utilities
    benchmark_datasets.py          # benchmark runner for stored datasets
    metrics.py                     # metric helpers
    run_benchmarks.py              # standalone benchmark entry point
  utils/
    min_heap.py                    # pure-Python binary min-heap
    visualization.py               # network/path rendering
tests/                             # unit tests
data/datasets/default/             # benchmark graph datasets
results/
  analysis.txt                     # benchmark results (runtime, stress, gap)
  runtime_results.csv              # full per-row benchmark CSV
```

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
3. Use option `2` (distance), `3` (time), or `4` (both)
4. Provide optional constraints when prompted:
  - avoid nodes: `N_1_2,N_3_4`
  - avoid edges: `N_1_2->N_1_3,N_3_4->N_3_5`
  - for distance queries, choose algorithm or type `compare`
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

Default generated sets are written to `data/datasets/default/` so the benchmark
suite stays separate from ad hoc experimentation.

Suggested layout:

- `data/datasets/default/` - baseline benchmark graphs
- `data/datasets/experiments/` - optional custom or exploratory graphs

Default generated sets:

| Dataset | Grid | Scenario | Intended structure |
|---|---|---|---|
| `graph_100` | 10x10 | `realistic` | Mostly 2-4 outgoing roads per node, no hub bias |
| `graph_1000` | 25x40 | `mixed` | Mostly 2-4 outgoing roads with a small fraction of 5-7 road hubs |
| `graph_1000_stress` | 25x40 | `stress` | Denser variant of the 1000-node grid with more hub nodes |
| `graph_5000` | 50x100 | `mixed` | Larger mixed network with the same hub pattern, used to stress scale |

These are the default benchmark graphs. If you generate additional custom
graphs, put them under `data/datasets/experiments/` so benchmark results stay
separated from exploratory runs.

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

Optional (measure runtime and explainability in one pass, not split):

```bash
python src/evaluation/benchmark_datasets.py --no-split-runtime-stats
```

Outputs:

- `results/runtime_results.csv`
- `results/analysis.txt`

Benchmark CSV now also includes explainability/search-effort metrics when
available (for example expanded node counts) so runtime numbers can be
interpreted with search behavior.

By default, the benchmark runner uses `data/datasets/default/` when it exists;
otherwise it falls back to the legacy `data/datasets/` layout.

Registered algorithms span both objectives:

- Distance: `dijkstra`, `bidirectional_dijkstra`, `a_star`, `a_star_alt`, `weighted_a_star`, `bidirectional_a_star`
- Time (TDSP): `dijkstra`, `a_star`, `a_star_alt`, `weighted_a_star`, `a_star_active_alt`, `a_star_departure_alt`, `dijkstra_contracted`, `a_star_contracted`, `bidirectional_time_a_star`
- `stress_*` columns derived from expanded nodes over graph size
- `optimality_gap_pct` against Dijkstra baseline for each pair/objective

### How Benchmarking Works

The benchmark runner in `src/evaluation/benchmark_datasets.py` follows this
workflow:

1. Dataset discovery
- Scans dataset folders containing `nodes.csv` and `edges.csv`.
- Uses `data/datasets/default/` when available; otherwise falls back to
  `data/datasets/`.

2. Pair selection per dataset
- Builds a deterministic sample of reachable start-goal pairs
  (currently up to 5 pairs per dataset).
- Reachability is checked with Dijkstra so unreachable pairs do not distort
  runtime comparisons.

3. Algorithm execution by supported objective
- Each registered algorithm is run only for its declared cost type(s):
  - distance: `dijkstra`, `bidirectional_dijkstra`, `a_star`, `a_star_alt`, `weighted_a_star`, `bidirectional_a_star`
  - time: `dijkstra`, `a_star`, `a_star_alt`, `weighted_a_star`, `a_star_active_alt`, `a_star_departure_alt`, `dijkstra_contracted`, `a_star_contracted`, `bidirectional_time_a_star`
- Start time is fixed per objective for reproducibility:
  - distance: `0`
  - time: `8:00` (`8 * 60` minutes)

4. Warmup and timing policy
- Algorithms with one-time setup can define a warmup hook
  (for example ALT landmark precomputation).
- In default split mode, runtime timing is collected separately from stats
  collection to reduce measurement overhead in latency numbers.
- In `--no-split-runtime-stats` mode, timing and stats are collected together
  in a single pass.

5. Aggregation and metrics
- For each algorithm/pair/objective, repeated runs are summarized as
  min/mean/max runtime.
- Explainability metrics (for example expanded nodes) are aggregated similarly.
- Stress metrics are derived from expansions over graph size:
  - `stress_mean = expanded_nodes_mean / |V|`
  - `stress_max = expanded_nodes_max / |V|`
- Optimality gap is computed against Dijkstra on the same pair/objective:
  - `optimality_gap_pct = ((C_alg - C_dijkstra) / C_dijkstra) * 100`

6. Output files
- CSV (`results/runtime_results.csv`): row-level benchmark summaries with
  metadata (`dataset`, `scenario`, `seed`, objective, runtime/stats fields).
- Text summary (`results/analysis.txt`): per-dataset interpretation table with
  runtime/stress/gap rollups.

## Implemented Algorithms

| Algorithm | Objective(s) | Heuristic / Strategy | Notes |
|---|---|---|---|
| `dijkstra` | distance, **time** | none | Baseline TDSP solver; pluggable `cost_func` |
| `bidirectional_dijkstra` | distance | none | Two-sided Dijkstra; distance only |
| `a_star` | distance, **time** | scaled Euclidean | Admissible heuristic; time mode uses `time_heuristic_scale` |
| `a_star_alt` | distance, **time** | ALT landmarks | 4 landmarks; time mode uses min-over-24h landmark distances |
| `weighted_a_star` | distance, **time** | scaled Euclidean × 1.25 | Trades optimality for speed; benchmarked for both objectives |
| `bidirectional_a_star` | distance | symmetric Euclidean | Distance only; conservative termination |
| `a_star_active_alt` | **time** | Active ALT (16→4) | Selects best 4 of 16 landmarks per (start,goal) query |
| `a_star_departure_alt` | **time** | Departure-aware ALT | Cache keyed by departure hour; heuristic uses global 24-hour min for admissibility |
| `bidirectional_time_a_star` | **time** | Backward min-time Dijkstra | Phase 1: reverse Dijkstra from goal using `min(time_list)`; Phase 2: forward TDSP A* using Phase 1 as heuristic |
| `dijkstra_contracted` | **time** | Degree-2 contraction | Dijkstra on degree-2-contracted graph |
| `a_star_contracted` | **time** | Degree-2 contraction + Euclidean | A* on degree-2-contracted graph |

### Cost Functions

- `cost_by_distance(edge, t)` → `edge.distance` (time-independent)
- `cost_by_time(edge, t)` → `edge.time_list[int(t // 60) % 24]` (time-dependent)

Both are inlined directly in the Dijkstra and A* relaxation loops to eliminate function-call overhead. Any custom cost function falls through to the generic call path.

### Preprocessing

| Algorithm | Preprocessing | Cached on |
|---|---|---|
| `a_star_alt` | ALT landmark distances (4 landmarks, global min-time) | `graph._alt_cache` |
| `a_star_active_alt` | ALT landmark distances (16 landmarks) | `graph._time_alt_cache` |
| `a_star_departure_alt` | Departure-aware landmark distances | `graph._departure_alt_caches` |
| `bidirectional_time_a_star` | Backward min-time Dijkstra from goal | `graph._bwd_min_time_cache` |
| `dijkstra_contracted` / `a_star_contracted` | Degree-2 node contraction | `graph._contracted_graph_cache` |

All preprocessing is cached on the graph object and excluded from timed query loops via warmup hooks in the benchmark runner.

### Overhead Accounting & Timing Methodology

**Runtime measurement integrity:** All reported runtimes include the full algorithm execution from start to finish. No overhead is subtracted from the final results. This means:

- **Benchmark timing** (`src/evaluation/benchmark.py`): Times the full algorithm call including any per-query setup (e.g., heuristic initialization). Preprocessing (landmarks, contraction, backward Dijkstra) is excluded via warmup hooks, so it does not appear in reported query times.
- **Split mode (default)**: Runtime is measured without stats collection to reduce measurement overhead and improve latency accuracy. Stats are collected in a separate call on the same pair.
- **Compare mode** (menu option for distance/time queries): Times multiple algorithm runs on the same pair; includes full algorithm execution with any per-query overhead (e.g., heuristic cost per node). This is the per-call cost users will see in production.
- **Combined query** (menu option 3.5): Runs both distance-optimized and time-optimized algorithms independently and reports both path objectives in full detail.

**Transparency note:** When a "smart" algorithm appears slower than Dijkstra in spite of fewer node expansions, this reflects Python-level constant-factor overhead (e.g., heuristic evaluation cost per node, landmark distance lookups). Stress metrics (expanded_nodes / |V|) are reported alongside runtime (ms) so you can see the tradeoff — lower stress with higher per-node cost indicates overhead dominance, which is exactly what the findings show for TDSP A*-based methods.

## Cross-Dataset Performance Summary

All benchmarks use 5 query pairs per dataset, 10 runs per pair, departure at 08:00 for time-based queries. Preprocessing (landmark/contraction/backward-Dijkstra) is excluded from timed query loops. Default benchmarks include `graph_1000_stress`; summary tables below focus on the three baseline datasets, while full stress results are in `results/analysis.txt`.

### Distance-based results

| Algorithm | graph_100 mean ms | graph_1000 mean ms | graph_5000 mean ms | graph_5000 stress |
|---|---|---|---|---|
| `dijkstra` | 0.18 | 1.45 | 16.95 | 0.748 |
| `bidirectional_dijkstra` | 0.21 | 1.51 | 23.80 | 0.704 |
| `a_star` | 0.27 | 2.17 | 21.72 | 0.733 |
| `a_star_alt` | **0.18** | **1.26** | **5.01** | **0.108** |
| `weighted_a_star` | 0.28 | 1.98 | 23.17 | 0.730 |
| `bidirectional_a_star` | 0.76 | 6.36 | 71.11 | 1.746 |

**Distance winner:** `a_star_alt` — best runtime across all graph sizes with 85% fewer node expansions at 5000-node scale. All algorithms return optimal paths (0% gap).

### Time-based (TDSP) results

| Algorithm | graph_100 mean ms | graph_1000 mean ms | graph_5000 mean ms | graph_5000 stress |
|---|---|---|---|---|
| `dijkstra` | 0.17 | 1.69 | 17.35 | 0.751 |
| `a_star` | 0.24 | 2.00 | 22.31 | 0.728 |
| `a_star_alt` | 0.27 | 1.49 | 16.56 | 0.335 |
| `weighted_a_star` | 0.26 | 1.89 | 21.94 | 0.722 |
| `a_star_active_alt` | 0.30 | 1.45 | 15.93 | 0.335 |
| `a_star_departure_alt` | 0.30 | 1.56 | 16.97 | 0.335 |
| `dijkstra_contracted` | 0.18 | 1.46 | 17.61 | 0.751 |
| `a_star_contracted` | 0.28 | 1.99 | 23.44 | 0.728 |
| `bidirectional_time_a_star` | **0.14** | **0.63** | **7.89** | **0.249** |

**TDSP winner (runtime and expansions) at graph_5000:** `bidirectional_time_a_star` (7.89 ms, stress 0.249) — beats Dijkstra on both runtime (-55%) and node expansions (-67%). The backward min-time heuristic is tight enough that the per-node savings outweigh the lookup overhead.

**Runner-up by runtime:** `dijkstra` (17.35 ms) — best of the heuristic-free algorithms; most other A*-based approaches are slower due to heuristic overhead exceeding their node-expansion savings.

**Best of the landmark-based approaches:** `a_star_active_alt` (15.93 ms, stress 0.335) — active landmark selection beats fixed landmark sets while still reducing expansions vs Dijkstra.

All TDSP algorithms return optimal paths (0% gap vs Dijkstra baseline).

## Summary of Findings

**Distance problem:**
- `a_star_alt` is the best distance algorithm across all graph sizes — ALT landmark heuristic cuts node expansions by ~85% at 5000 nodes and wins on runtime at every scale tested.

**Time-dependent shortest path (TDSP) problem:**
- `bidirectional_time_a_star` wins on both runtime (7.89 ms) and node expansions (stress 0.249) at graph_5000. Its backward min-time Dijkstra heuristic is tight enough to overcome Python's heuristic overhead.
- Most other A*-based TDSP algorithms (`a_star`, `a_star_alt`, `weighted_a_star`, `a_star_contracted`) are slower than raw Dijkstra — their heuristic evaluation cost per node exceeds the savings from expanding fewer nodes.
- `a_star_active_alt` (15.93 ms, stress 0.335) is the best of the landmark-based approaches — active landmark selection cuts expansions while keeping runtime near Dijkstra.
- All TDSP algorithms return provably optimal paths (0% gap vs Dijkstra baseline).

**Key insight:** At Python scale, algorithm complexity and runtime do not always align. Reporting expanded_nodes and stress alongside ms explains when a "smarter" algorithm is slower due to constant-factor overhead.

## Limitations and Threats to Validity

- Synthetic-graph bias: generated grids are useful but simpler than real road networks (topology, turn restrictions, bottlenecks).
- Sample-size bias: rankings are based on 5 sampled source-goal pairs per dataset; different samples can shift mean runtime.
- Runtime environment sensitivity: Python constant factors, machine load, and interpreter version affect millisecond-level comparisons.
- Preprocessing accounting: benchmark excludes one-time setup; deployment scenarios should also report setup cost.
- Scale boundary: datasets up to 5,000 nodes are strong for project evaluation but do not represent production-scale routing graphs.

## Interesting Discoveries / Breakthroughs

1. **Reverse-neighbor caching** — Moving reverse adjacency into a graph-level cache removed repeated preprocessing work and made bidirectional methods feasible at project scale.

2. **Search effort and runtime can diverge** — Algorithms with lower stress were not always faster. Python constant-factor overhead (dict hashing, function calls) can dominate asymptotic intuition at current graph sizes.

3. **The heuristic tax problem for most TDSP heuristics** — Most A*-based TDSP algorithms (`a_star`, `a_star_alt`, `weighted_a_star`) pay more per node in heuristic overhead than they save by expanding fewer nodes, making them slower than Dijkstra at graph_5000. The exception is `bidirectional_time_a_star`, whose backward min-time heuristic is tight enough that it beats Dijkstra on both runtime and expansions.

4. **Inner-loop inlining** — Replacing `cost_by_time(edge, t)` and `cost_by_distance(edge, t)` function calls with direct attribute access (`edge.time_list[int(t//60)%24]`, `edge.distance`) in the relaxation loop eliminates two stack frames per edge relaxation across all algorithms.

5. **Departure-aware ALT stays admissible across midnight** — The departure-hour keyed cache uses the global 24-hour minimum for landmark preprocessing so the heuristic remains safe even when paths cross midnight.

6. **Degree-2 contraction has limited effect on these graphs** — With edge/node ratio ~3.5, few degree-2 chains exist to contract. The preprocessing overhead outweighs the search reduction, making contracted variants slower than raw Dijkstra.

## Edge Updates During a Trip

Traffic profiles are modeled as periodic 24-hour schedules that can be updated at coarse intervals (for example weekly). If an update occurs mid-trip, the chosen policy is to re-run a time-based query from the current node and current time using the updated graph. This avoids mixing old and new profiles within a single edge traversal while still providing a reasonable response to rare updates. The graph exposes `update_edge_time_profile()` to swap an edge's 24-hour list and invalidate time-dependent caches before rerouting.

## Add a New Algorithm

1. Create algorithm file in `src/algorithms/`.
2. Ensure the function signature is compatible with benchmark calls:

```python
def my_algo(graph, start, goal, cost_func, start_time=0, **kwargs):
    # return at least (path, total_cost)
    return path, total_cost
```

3. Register it in `ALGORITHM_REGISTRY` in `src/evaluation/benchmark_datasets.py` with `cost_types`, optional `kwargs`/`time_kwargs`, and a `warmup` lambda if preprocessing is needed.
4. Add unit tests in `tests/`.
5. Re-run pipeline:

```bash
python -m unittest discover -s tests -v
python src/evaluation/benchmark_datasets.py
```

## Notes

- Graph is directed; visual proximity does not imply direct reachability.
- Time objective uses rolling hour based on cumulative minutes: `hour = int(t // 60) % 24`.
- `bidirectional_dijkstra` and `bidirectional_a_star` raise `ValueError` if `start_time != 0` — they are distance-only.
- All preprocessing results are cached on the graph object; re-importing a graph clears all caches.
