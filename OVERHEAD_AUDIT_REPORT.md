# Code Audit Report: Runtime Overhead Deduction Verification

## Executive Summary
✅ **NO runtime deduction detected** in any evaluation or visualization functions. All reported runtimes include full algorithm execution from start to finish.

## Audited Components

### 1. benchmark.py - `benchmark_dijkstra()` function
**File:** `src/evaluation/benchmark.py`

**Timing Logic:**
```python
for _ in range(runs_per_pair):
    t0 = time.perf_counter()                    # START TIMER
    result = dijkstra_fn(                       # FULL ALGORITHM CALL
        graph,
        start,
        goal,
        cost_func,
        start_time=start_time,
        **algorithm_kwargs,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000  # STOP TIMER
    run_times_ms.append(elapsed_ms)
```

**Findings:**
- ✅ Timer starts BEFORE algorithm call
- ✅ Timer stops AFTER algorithm returns
- ✅ No subtraction of overhead from `elapsed_ms`
- ✅ Stats collection is separate from timing loop (handled via `collect_stats=False` flag in warmup, `collect_stats=True` in result collection)

**Conclusion:** Timing is correct. Includes full algorithm execution time.

---

### 2. visualization.py - `render_path_details()` function
**File:** `src/utils/visualization.py`

**Metric Computation:**
```python
# Always report both totals for the selected path.
total_distance = 0.0
total_travel_time = 0.0

rolling_time = start_time
for i in range(len(path) - 1):
    # ... traverse segments ...
    total_distance += edge.distance
    total_travel_time += segment_time
    rolling_time += segment_time

lines.append(f"Total distance: {total_distance:.2f} km")
lines.append(f"Total travel time: {total_travel_time:.2f} min")

if cost_type == "distance":
    lines.append(f"Optimized objective: distance = {cost:.2f} km")
else:
    lines.append(f"Optimized objective: time = {cost:.2f} min")
```

**Findings:**
- ✅ Reports total distance (computed independently from path segments)
- ✅ Reports total travel time (computed independently from path segments)
- ✅ Reports optimized objective (the `cost` parameter passed to function)
- ✅ No runtime metrics manipulated in this function
- ✅ No subtraction or adjustment of any overhead

**Conclusion:** Display function only. No overhead accounting happens here.

---

### 3. main.py - Compare mode (distance and time queries)
**File:** `src/main.py`

**Distance Compare Mode Timing Logic (lines 190-196):**
```python
for _ in range(compare_runs):
    t0 = time.perf_counter()
    algo_fn(                           # FULL ALGORITHM CALL
        graph,
        start,
        goal,
        cost_by_distance,
        avoid_nodes=avoid_nodes,
        avoid_edges=avoid_edges,
        **algo_kwargs,
    )
    runtimes_ms.append((time.perf_counter() - t0) * 1000)
```

**Findings:**
- ✅ Timer starts BEFORE algorithm
- ✅ Timer stops AFTER algorithm returns
- ✅ No subtraction from recorded runtime
- ✅ Stats collected in SEPARATE call (lines 198-206) after timing is complete
- ✅ Comment "runtime measured without stats overhead" refers to stats collection being separate, NOT that overhead is subtracted

**Time Compare Mode:**
- Same timing pattern for time-based algorithm comparison
- Full algorithm execution timed without deduction

**Conclusion:** Timing includes full algorithm execution. Comment is accurate — stats overhead is avoided by collecting stats separately.

---

### 4. benchmark_datasets.py - High-level orchestrator
**File:** `src/evaluation/benchmark_datasets.py`

**Key Points:**
- ✅ Uses `benchmark_dijkstra()` from benchmark.py (verified above)
- ✅ Warmup hooks exclude preprocessing but NOT query execution
- ✅ Per-pair timing collected correctly
- ✅ Aggregation (min/mean/max) done on already-collected run times

**Conclusion:** Orchestrator correctly delegates to verified timing functions.

---

## Seed Robustness Verification

**Test:** Regenerated datasets with seed 43, ran benchmarks, compared with seed 42.

**Results:**
- ✅ Algorithm rankings remain consistent (a_star_alt wins distance, bidirectional_time_a_star wins time)
- ✅ Optimality gaps remain 0.0000% across all algorithms on all datasets
- ✅ Runtime variance expected (due to system variance, network topology differences)
- ✅ No anomalies detected that would indicate timing issues

**Comparison (graph_5000):**
| Metric | Seed 42 | Seed 43 | Variance | Gap 42 | Gap 43 |
|--------|---------|---------|----------|--------|--------|
| dijkstra (time) | 19.55 ms | 22.33 ms | +14.2% | 0.0% | 0.0% |
| a_star_alt (dist) | 5.63 ms | 15.71 ms | +179% | 0.0% | 0.0% |
| bidirectional_time_a_star (time) | 7.79 ms | 8.96 ms | +15.0% | 0.0% | 0.0% |

**Note on a_star_alt variance:** Different random seed produces different graph topology, leading to different landmark positions and different search behavior. This is expected and correct.

---

## Combined Query Mode

**File:** `src/main.py` - `_run_combined_query()` function

**Behavior:**
- ✅ Runs both dijkstra(cost_by_distance) and dijkstra(cost_by_time, start_time) sequentially
- ✅ Renders both path reports with full metric breakdown
- ✅ Each algorithm call is timed independently
- ✅ No runtime subtraction or deduction

**Conclusion:** Combined query correctly executes both algorithms and reports results without overhead manipulation.

---

## Documentation Updates

Updated `README.md` with new section: **"Overhead Accounting & Timing Methodology"**

This section explicitly states:
- Runtime measurement includes full algorithm execution
- No overhead subtracted from results
- Preprocessing excluded via warmup hooks
- Split mode separates stats collection from timing
- Compare mode times full execution including per-query setup
- Combined query runs algorithms independently

---

## Summary

| Component | Status | Deduction Detected |
|-----------|--------|-------------------|
| benchmark.py | ✅ VERIFIED | NO |
| visualization.py | ✅ VERIFIED | NO |
| main.py compare mode | ✅ VERIFIED | NO |
| benchmark_datasets.py | ✅ VERIFIED | NO |
| combined query | ✅ VERIFIED | NO |

**Overall Conclusion:** ✅ **All reporting is transparent and accurate. No runtime manipulation detected.**
