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

Recent additions include:

- `a_star` (distance objective)
- `a_star_alt` (distance objective, ALT landmark heuristic)
- `weighted_a_star` (distance objective, faster but may be suboptimal)
- `bidirectional_a_star` (distance objective)
- `stress_*` columns derived from expanded nodes over graph size
- `optimality_gap_pct` against Dijkstra baseline for each pair/objective

## Implemented Approaches (Current)

| Algorithm | Objective(s) | Explainability Stats | Notes |
|---|---|---|---|
| `dijkstra` | distance, time | `expanded_nodes` | Baseline for cost optimality and gap calculations |
| `bidirectional_dijkstra` | distance | `expanded_forward`, `expanded_backward`, `expanded_nodes` | Uses reverse-adjacency cache |
| `a_star` | distance | `expanded_nodes` | Uses scaled Euclidean heuristic |
| `a_star_alt` | distance | `expanded_nodes` | Uses ALT landmarks; warmup preprocessing excluded from timed query loops |
| `weighted_a_star` (`w=1.25`) | distance | `expanded_nodes` | Speed/quality tradeoff variant |
| `bidirectional_a_star` | distance | `expanded_forward`, `expanded_backward`, `expanded_nodes` | Conservative termination for correctness |

## Cross-Dataset Performance Interpretation

Using current `results/analysis_default.txt` from the isolated default suite
(`runs-per-pair = 1`):

### graph_100

- Runtime leader: `dijkstra` (`0.3907 ms` mean)
- Lowest stress: `a_star_alt` (`0.3280` mean)
- Observation: ALT reduces explored nodes strongly, but small-graph runtime can
  still favor low-overhead baselines

### graph_1000

- Runtime leader: `a_star_alt` (`2.6147 ms` mean)
- Lowest stress: `a_star_alt` (`0.1524` mean)
- Observation: ALT landmark heuristic outperformed baseline distance methods on
  medium graph size while maintaining `0%` gap

### graph_5000

- Runtime leader: `a_star_alt` (`9.5330 ms` mean)
- Lowest stress: `a_star_alt` (`0.1075` mean)
- Observation: ALT gives a major large-graph breakthrough, reducing both
  expansion workload and query runtime substantially

### Quality (Optimality Gap)

- Reported mean/max gap is effectively `0.0000%` for all currently evaluated
  distance algorithms in this run
- Practical interpretation: current heuristic configuration remains strongly
  conservative, so weighted mode is not yet showing measurable quality loss

### Why ALT Can Lose on Some Individual Queries

- Fixed per-query overhead: ALT must evaluate landmark-based heuristic bounds
  for many candidate nodes; for short/local routes this extra work can dominate.
- Small search region effect: when source and destination are close, Dijkstra
  variants may finish quickly before heuristic guidance has much chance to help.
- Directional/topology effect: some local structures are naturally favorable to
  bidirectional meeting, making bidirectional Dijkstra very competitive.

Practical interpretation: single-pair compare tables are useful for local
behavior, while dataset-level averages are the right source for overall method
ranking.

## Summary of Findings

This is the short version of the distance-routing story so far.

- `dijkstra` is the safest baseline and still the best choice on very small
  graphs when setup overhead matters more than search reduction.
- `a_star` with the default Euclidean heuristic is correct, but the heuristic
  is not strong enough to produce a consistent runtime win in this codebase.
- `a_star_alt` is the strongest distance algorithm overall for the current
  generated datasets because its landmark heuristic cuts search effort enough
  to win on medium and large graphs.
- `bidirectional_dijkstra` can reduce explored nodes, but that does not always
  translate into faster runtime.
- `bidirectional_a_star` is currently a correctness-oriented experimental
  method rather than a practical performance winner.
- The main evaluation lesson is that runtime, search effort, and optimality
  must be reported together; node expansions alone do not tell the full story.
- A separate verification run on the isolated default suite in
  `data/datasets/default/` preserved the same qualitative ranking: Dijkstra is
  still the safest tiny-graph baseline, and ALT remains the best distance
  method on the medium/large graphs.

## Interesting Discoveries / Breakthroughs

1. Reverse-neighbor caching was a structural breakthrough
- Moving reverse adjacency into graph-level cache removed repeated preprocessing
  work and made bidirectional methods feasible at project scale.

2. Search effort and runtime can diverge materially
- Across datasets, algorithms with lower stress were not always faster.
- This revealed that implementation overhead and Python-level constant factors
  can dominate asymptotic intuition at current graph sizes.

3. Weighted A* can remain effectively optimal with conservative heuristics
- With current admissible scaling, weighted A* did not produce visible gap in
  this benchmark pass.
- This is useful for safety, but indicates additional heuristic engineering is
  needed to expose stronger speed-vs-quality tradeoffs.

4. ALT landmarks changed the distance-routing frontier
- With warmup preprocessing separated from timed loops, `a_star_alt` became the
  best performer on medium and large datasets while preserving `0%` gap.
- This demonstrates that stronger heuristic quality can beat baseline Dijkstra
  when measurement avoids mixing one-time setup with per-query runtime.

Benchmark runner evaluates each registered algorithm for its supported objectives:

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

Implementation detail used here: Euclidean heuristics are scaled by a safe
graph-derived factor so the default distance A* heuristic remains admissible
on generated datasets.

### Weighted A*

Weighted A* uses:

$$
f(n) = g(n) + w \cdot h(n), \quad w \ge 1
$$

With larger $w$, search is greedier and often faster, but optimality is not
guaranteed. This project includes `weighted_a_star` for explicit speed/quality
tradeoff experiments.

### Bidirectional A*

`bidirectional_a_star` is implemented for distance routing with symmetric
heuristics:

- forward side estimates from current node to goal
- backward side estimates from current node to start

To avoid incorrect aggressive early-stop behavior from incompatible potentials,
the implementation uses conservative termination while still applying heuristic
ordering on both frontiers.

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

## Final Distance-Evaluation Sweep (Sanity Check)

This section summarizes whether the current implementation is sufficient to
accurately evaluate the shortest-distance problem for this project scope.

### What is implemented and validated

- Baseline + comparators are implemented for distance objective:
  `dijkstra`, `bidirectional_dijkstra`, `a_star`, `a_star_alt`,
  `weighted_a_star`, `bidirectional_a_star`
- Correctness and behavior tests pass (`43/43`), including:
  - path/cost validity checks
  - unreachable behavior
  - avoid-node and avoid-edge constraints
  - explainability stats shape/availability
- Benchmark outputs include:
  - runtime (`mean/max`)
  - search effort (`expanded_nodes`, `stress`)
  - quality (`optimality_gap_pct` vs Dijkstra)
- Benchmark methodology separates query latency from stats overhead by default
  (split runtime/stats mode), and excludes one-time ALT preprocessing from the
  timed query loop via warmup.

### Tradeoffs and realistic algorithm choices

- Small graphs (`graph_100`):
  `dijkstra` is still the fastest practical default due to lower constant
  overhead, even when ALT explores fewer nodes.
- Medium and large graphs (`graph_1000`, `graph_5000`):
  `a_star_alt` is the most realistic distance-routing choice in this codebase,
  with major runtime gains and much lower stress while keeping near-zero gap.
- `weighted_a_star` currently behaves close to optimal in these datasets
  (observed gap near `0%`), so it has not yet exposed a strong speed-quality
  frontier under the present heuristic configuration.
- `bidirectional_a_star` is currently not a practical runtime winner in this
  implementation; keep it as an experimental/reference method.

### What this means for evaluation confidence

- For shortest-distance comparisons in this project, the setup is now strong
  enough to make fair algorithm rankings and defend conclusions with runtime,
  workload, and quality evidence.
- The primary caveat is external validity: datasets are synthetic and currently
  benchmarked on a fixed pair sample. Conclusions are accurate for this
  benchmark design and implementation, but should be generalized to real-world
  networks with care.

## Limitations and Threats to Validity

- Synthetic-graph bias:
  generated grids with realistic tuning are useful, but still simpler than
  irregular real road networks (topology, turn restrictions, bottlenecks,
  long-tail edge weights).
- Sample-size bias in query pairs:
  dataset-level rankings are based on a fixed sampled set of source-goal pairs;
  different samples can shift mean runtime and tail behavior.
- Runtime environment sensitivity:
  Python constant factors, machine load, and interpreter version can affect
  micro/millisecond-level comparisons, especially on smaller graphs.
- Preprocessing accounting choices:
  split mode intentionally emphasizes steady-state query latency; if a method
  requires one-time setup, deployment scenarios should also report setup cost.
- Scale boundary:
  current datasets (up to 5,000 nodes) are strong for project evaluation but do
  not fully represent very large production routing graphs.

## Potential Improvements (Distance Problem)

These improvements are prioritized for better evaluation quality and stronger
distance-routing performance.

### 1. Strengthen benchmark rigor

- Increase `runs_per_pair` and sampled pair count per dataset.
- Add repeated benchmark trials with different random seeds.
- Report variance and percentile tails (for example p90/p95/p99), not only
  mean/max.

Why this matters:
reduces sensitivity to outliers and improves confidence in speed rankings.

### 2. Separate query and preprocessing costs explicitly

- Add explicit benchmark outputs for:
  - one-time preprocessing time per algorithm/dataset (for example ALT setup)
  - post-warmup query runtime

Why this matters:
supports realistic deployment decisions where rebuild frequency varies.

### 3. Tune ALT and weighted parameters systematically

- Run sweeps for `landmark_count` (for example 2/4/8/16).
- Run sweeps for `heuristic_weight` (for example 1.0/1.1/1.25/1.5).
- Publish Pareto-style summary: runtime vs optimality gap vs stress.

Why this matters:
makes speed-quality tradeoffs explicit instead of relying on a single setting.

### 4. Improve bidirectional A* practicality

- Investigate compatible-potential termination and reduced bookkeeping.
- Compare against unidirectional ALT under identical test workloads.
- Keep correctness tests strict while optimizing constant overhead.

Why this matters:
current implementation is correctness-oriented but not yet runtime-competitive.

### 5. Expand distance realism in datasets

- Add more heterogeneous structures: sparse corridors, dense downtown cores,
  bridge-like chokepoints, disconnected neighborhood patterns.
- Validate edge-weight distributions against intended scenario assumptions.

Why this matters:
improves external validity of algorithm rankings for realistic shortest-distance
analysis.

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