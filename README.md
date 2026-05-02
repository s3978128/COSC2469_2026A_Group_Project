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

By default the generator now writes to the top-level `data/datasets/` directory.
To keep a stable baseline for README reporting, keep an archived snapshot under
`data/datasets/default/` and place exploratory or CLI-generated runs under
`data/datasets/experiments/` or a seed-specific folder such as
`data/datasets/seed43/`.

Suggested layout:

- `data/datasets/default/` - baseline benchmark graphs (archive for README)
- `data/datasets/experiments/` - optional custom or exploratory graphs
- `data/datasets/seed43/` - example seeded generation used for robustness checks

Default generated sets (baseline):

| Dataset | Grid | Scenario | Intended structure |
|---|---|---|---|
| `graph_100` | 10x10 | `realistic` | Mostly 2-4 outgoing roads per node, no hub bias |
| `graph_1000` | 25x40 | `mixed` | Mostly 2-4 outgoing roads with a small fraction of 5-7 road hubs |
| `graph_1000_stress` | 25x40 | `stress` | Denser variant of the 1000-node grid with more hub nodes |
| `graph_5000` | 50x100 | `mixed` | Larger mixed network with the same hub pattern, used to stress scale |

These are the default benchmark graphs (baseline). If you generate additional
custom graphs, put them under `data/datasets/experiments/` or a seeded folder
so benchmark results stay separated from the archived baseline used in the
README.

Example: generate a seeded experimental suite into `data/datasets/seed43/`:

```bash
python src/generator/generate_datasets.py --seed 43 --base-dir data/datasets/seed43
```

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

Archived benchmark snapshots:

- `results/analysis_default.txt`: the default dataset suite under `data/datasets/default/`
- `results/analysis_seed43.txt`: the same suite regenerated with seed `43` for a robustness check
- `results/analysis_cli.txt`: benchmark of the top-level CLI-generated datasets (data/datasets/)

Snapshot CSVs:

- `results/runtime_results_default.csv`
- `results/runtime_results_seed43.csv`

Row-level CSV outputs for CLI runs are also saved alongside other results, e.g. `results/runtime_results_cli.csv`.

Benchmark CSV now also includes explainability/search-effort metrics and
one-time preprocessing costs (`preprocess_ms`) when
available (for example expanded node counts) so runtime numbers can be
interpreted with search behavior.

The corresponding row-level CSV outputs live in `results/` alongside the analysis files.

All analysis files include the full algorithm set for each supported objective and every dataset discovered by the runner for that snapshot. The current default suite covers `graph_100`, `graph_1000`, `graph_1000_stress`, and `graph_5000`.

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
- **Preprocessing measurement**: One-time setup is timed separately and stored as `preprocess_ms` in the CSV and as `preprocess:` lines in the analysis text.
- **Split mode (default)**: Runtime is measured without stats collection to reduce measurement overhead and improve latency accuracy. Stats are collected in a separate call on the same pair.
- **Compare mode** (menu option for distance/time queries): Times multiple algorithm runs on the same pair; includes full algorithm execution with any per-query overhead (e.g., heuristic cost per node). This is the per-call cost users will see in production.
- **Combined query** (menu option 3.5): Runs both distance-optimized and time-optimized algorithms independently and reports both path objectives in full detail.

**Transparency note:** When a "smart" algorithm appears slower than Dijkstra in spite of fewer node expansions, this reflects Python-level constant-factor overhead (e.g., heuristic evaluation cost per node, landmark distance lookups). Stress metrics (expanded_nodes / |V|) are reported alongside runtime (ms) so you can see the tradeoff — lower stress with higher per-node cost indicates overhead dominance, which is exactly what the findings show for TDSP A*-based methods.

## Cross-Dataset Performance Summary

All benchmarks use 5 query pairs per dataset, 10 runs per pair, departure at 08:00 for time-based queries. Preprocessing (landmark/contraction/backward-Dijkstra) is excluded from timed query loops and reported separately via `preprocess_ms`. The summary below covers every dataset in both the default archive and the seed-43 robustness run.

### Best Performers By Dataset

| Dataset | Default best distance | Default best TDSP | Seed43 best distance | Seed43 best TDSP |
|---|---|---|---|---|
| `graph_100` | `a_star_alt` - 0.19 ms, stress 0.328 | `bidirectional_time_a_star` - 0.17 ms, stress 0.456 | `a_star_alt` - 0.16 ms, stress 0.242 | `bidirectional_time_a_star` - 0.15 ms, stress 0.434 |
| `graph_1000` | `a_star_alt` - 1.25 ms, stress 0.152 | `bidirectional_time_a_star` - 0.62 ms, stress 0.145 | `a_star_alt` - 0.64 ms, stress 0.086 | `bidirectional_time_a_star` - 0.48 ms, stress 0.115 |
| `graph_1000_stress` | `a_star_alt` - 1.22 ms, stress 0.071 | `bidirectional_time_a_star` - 0.88 ms, stress 0.153 | `a_star_alt` - 0.99 ms, stress 0.089 | `bidirectional_time_a_star` - 1.12 ms, stress 0.190 |
| `graph_5000` | `a_star_alt` - 5.41 ms, stress 0.108 | `bidirectional_time_a_star` - 7.59 ms, stress 0.249 | `a_star_alt` - 12.98 ms, stress 0.290 | `bidirectional_time_a_star` - 8.11 ms, stress 0.252 |

### Distance Results

The distance benchmark is consistently won by `a_star_alt` for every dataset in both runs. The landmark heuristic dominates once preprocessing is amortized, even on mid-sized graphs.

| Dataset | Default winner | Seed43 winner |
|---|---|---|
| `graph_100` | `a_star_alt` | `a_star_alt` |
| `graph_1000` | `a_star_alt` | `a_star_alt` |
| `graph_1000_stress` | `a_star_alt` | `a_star_alt` |
| `graph_5000` | `a_star_alt` | `a_star_alt` |

### TDSP Results

`bidirectional_time_a_star` is the best TDSP performer across every dataset in both the default and seed-43 runs. It is the only TDSP method that is both consistently fast and consistently low-stress at every scale we benchmarked.

| Dataset | Default winner | Seed43 winner |
|---|---|---|
| `graph_100` | `bidirectional_time_a_star` | `bidirectional_time_a_star` |
| `graph_1000` | `bidirectional_time_a_star` | `bidirectional_time_a_star` |
| `graph_1000_stress` | `bidirectional_time_a_star` | `bidirectional_time_a_star` |
| `graph_5000` | `bidirectional_time_a_star` | `bidirectional_time_a_star` |

### Insights Gained

- `a_star_alt` is the most reliable distance algorithm overall, especially once the graph gets denser or larger.
- `bidirectional_time_a_star` is the only TDSP method that stays ahead of Dijkstra at every dataset size we tested.
- `graph_1000_stress` is a useful stress case because it shows the biggest gap between plain Dijkstra and ALT-based search effort.
- Preprocessing costs scale with graph size (e.g., ALT ~448 ms and active ALT ~969 ms on `graph_5000` in the default run), so those methods pay off when amortized across repeated queries.
- Seed changes alter absolute timings, but the top-level ranking remains stable, which is what we want for README reporting.
- Lower stress does not always mean lower runtime; Python overhead still matters, especially for the more elaborate heuristic variants.

## Summary of Findings

**Distance problem:**
- `a_star_alt` is the best overall distance performer across the full default suite and remains the fastest distance method in the seed-43 run as well.
- It wins because ALT landmarks sharply reduce node expansions, which matters more than per-node overhead once the graphs get larger.
- `bidirectional_dijkstra` remains competitive on mid-sized graphs, but it is usually edged out by ALT once preprocessing is amortized.

**Time-dependent shortest path (TDSP) problem:**
- `bidirectional_time_a_star` is the best overall TDSP performer in both the default and seed-43 benchmark runs.
- It wins because the backward min-time search gives a tighter admissible heuristic, so the reduced search effort outweighs the extra bidirectional bookkeeping.
- Most other A*-based TDSP algorithms (`a_star`, `weighted_a_star`, `a_star_active_alt`, `a_star_departure_alt`, `a_star_contracted`) are slower than raw Dijkstra in the larger graphs because their heuristic cost per node is still high relative to the pruning they achieve.
- `a_star_alt` and `a_star_active_alt` remain useful as lower-stress TDSP options, but they are usually best interpreted as search-effort reducers rather than pure runtime winners.
- All TDSP algorithms return provably optimal paths (0% gap vs Dijkstra baseline).

**Robustness check:** The seed-43 run preserves the same overall winners as the default suite: `a_star_alt` for distance and `bidirectional_time_a_star` for TDSP. The absolute timings change because the generated graph topology changes with the seed, but the relative ranking stays stable.

**Key insight:** At Python scale, algorithm complexity and runtime do not always align. Reporting expanded_nodes and stress alongside ms explains when a "smarter" algorithm is slower due to constant-factor overhead.

## Limitations and Threats to Validity

- Synthetic-graph bias: generated grids are useful but simpler than real road networks (topology, turn restrictions, bottlenecks).
- Sample-size bias: rankings are based on 5 sampled source-goal pairs per dataset; different samples can shift mean runtime.
- Runtime environment sensitivity: Python constant factors, machine load, and interpreter version affect millisecond-level comparisons.
- Preprocessing accounting: one-time setup is excluded from per-query timing but reported separately as `preprocess_ms`.
- Scale boundary: datasets up to 5,000 nodes are strong for project evaluation but do not represent production-scale routing graphs.

## Interesting Discoveries / Breakthroughs

1. **Reverse-neighbor caching** — Moving reverse adjacency into a graph-level cache removed repeated preprocessing work and made bidirectional methods feasible at project scale.

2. **Search effort and runtime can diverge** — Algorithms with lower stress were not always faster. Python constant-factor overhead (dict hashing, function calls) can dominate asymptotic intuition at current graph sizes.

3. **The heuristic tax problem for most TDSP heuristics** — Most A*-based TDSP algorithms (`a_star`, `a_star_alt`, `weighted_a_star`) pay more per node in heuristic overhead than they save by expanding fewer nodes, making them slower than Dijkstra at graph_5000. The exception is `bidirectional_time_a_star`, whose backward min-time heuristic is tight enough that it beats Dijkstra on both runtime and expansions.

4. **Inner-loop inlining** — Replacing `cost_by_time(edge, t)` and `cost_by_distance(edge, t)` function calls with direct attribute access (`edge.time_list[int(t//60)%24]`, `edge.distance`) in the relaxation loop eliminates two stack frames per edge relaxation across all algorithms.

## Key Observations & Recommendations

- **Top performers (default archived datasets):** `a_star_alt` is the best distance algorithm across the default suite; `bidirectional_time_a_star` is the best TDSP algorithm. These winners are derived from the archived baseline run in `data/datasets/default/` and summarized in [results/analysis_default.txt](results/analysis_default.txt).
- **Preprocessing must be reported separately:** one-time costs (landmarks, contraction, backward Dijkstra) are now recorded as `preprocess_ms` in the CSV and as `preprocess:` lines in the analysis text. Always publish both the raw per-query mean and the one-time preprocess_ms.
- **Amortize expensive preprocessing when making claims about latency:** show an amortized per-query preprocessing cost (preprocess_ms / N_queries) for realistic query volumes. For example, ALT preprocessing on `graph_5000` (~448 ms) becomes ~0.45 ms/query at 1,000 queries.
- **Report cold-start and warm-start metrics:** include (a) cold-start end-to-end latency that includes preprocessing, (b) warm-start per-query latency excluding preprocessing, and (c) memory footprint of precomputed structures (landmark tables, contracted graphs, etc.).
- **Provide break-even points:** for each algorithm compare the amortized preprocessing + per-query time against a baseline (e.g., `dijkstra`) and report N_min (number of queries after which the preprocessed method becomes faster). This is the most actionable way to recommend an algorithm for production workloads.
- **When benchmarking, always include search-effort metrics:** expanded nodes and stress (expanded / |V|) explain when an algorithm's lower expansions don't translate to lower runtime due to Python-level overheads.
- **Practical deployment guidance:**
  - Use heavy-preprocessing methods (`a_star_alt`, `a_star_active_alt`, contraction) for server-side cached graphs where thousands of queries are expected.
  - Use lightweight or no-preprocess methods (`dijkstra`, `a_star` without ALT) for ad-hoc, single-shot queries or low-memory environments.
  - Include persistence/load-time of precomputed indexes in deployment cost calculations if indexes are saved to disk.

These recommendations reflect the current archived baseline results under `data/datasets/default/` and the updated analysis in `results/analysis_default.txt`.

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
