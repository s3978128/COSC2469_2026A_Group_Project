# Time Problem Fixes

## What Was Fixed

### 1. Departure-aware ALT correctness

Issue:
- The departure-aware ALT heuristic used `min(time_list[departure_hour:])` as a lower bound.
- That was not always admissible when paths crossed midnight.

Fix:
- The heuristic now uses the global 24-hour minimum travel time per edge.
- The `departure_hour` parameter remains for API compatibility and cache-keying, but it no longer changes the heuristic bound.

Effect:
- `a_star_departure_alt` is now correct again for time-dependent routing.
- The method should be described as a departure-keyed ALT variant, not a tighter departure-aware bound.

### 2. Contraction wrappers and avoid constraints

Issue:
- `dijkstra_contracted` and `a_star_contracted` could bypass `avoid_nodes` / `avoid_edges` because shortcuts can skip contracted intermediate nodes.

Fix:
- When avoid constraints are present, the wrappers now fall back to the original graph instead of using the contracted graph.

Effect:
- Constrained queries remain correct.
- Unconstrained queries can still benefit from contraction.

### 3. Regression coverage added

Added tests in `tests/test_time_algorithms.py` for:
- departure-alt correctness across midnight
- contracted Dijkstra respecting avoid nodes
- contracted A* respecting avoid nodes

### 4. Benchmark fairness for cached time algorithms

Issue:
- Some time algorithms include substantial one-time cache setup.
- `bidirectional_time_a_star` can look much slower on first query because it
	builds a backward min-time cache for each goal.

Fix:
- Added benchmark warmup for A*/Weighted-A* heuristic-scale caches.
- Added goal-wise prewarm for `bidirectional_time_a_star` using sampled pairs.
- Aligned departure-hour ALT benchmark kwargs with the benchmark's
	`--departure-hour` setting.

Effect:
- Time benchmark comparisons now better reflect steady-state query cost.
- The reported runtime ranking is less sensitive to first-call initialization.

### 5. CLI time compare coverage and fairness

Issue:
- CLI time compare covered only a subset of time algorithms and had warmup
	asymmetry across methods.

Fix:
- Time compare now includes:
	- `dijkstra`
	- `a_star`
	- `a_star_alt`
	- `a_star_active_alt`
	- `a_star_departure_alt`
	- `weighted_a_star`
	- `dijkstra_contracted`
	- `a_star_contracted`
	- `bidirectional_time_a_star`
- Added cache prewarm in compare mode for time heuristic scale, ALT caches,
	departure-keyed ALT cache, contraction cache, and bidirectional-time
	backward cache for the selected goal.

Effect:
- CLI compare output is now much closer to benchmark methodology and is a more
	reliable local sanity-check.

## Remaining Notes

- `a_star_departure_alt` retains `departure_hour` mainly for cache-key and API
	consistency; since the heuristic bound is now global-min for correctness,
	it should not be interpreted as a tighter bound variant.
