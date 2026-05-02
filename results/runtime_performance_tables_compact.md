# Archived Runtime Performance Tables

This report combines the two archived benchmark suites (`default` and `seed43`). Rows are sorted by mean runtime within each dataset-suite, so rank 1 is the fastest algorithm for that dataset/problem. Preprocessing is included explicitly in the `Preprocess (ms)` column and reported as `N/A` when an algorithm has no one-time setup.

## Distance Problem

| Suite | Dataset | Rank | Algorithm | Mean runtime (ms) | Max runtime (ms) | Preprocess (ms) | Expanded nodes mean | Stress mean | Optimality gap mean |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| `default` | `graph_100` | 1 | `a_star_alt` | 0.1901 | 0.2711 | 4.6539 | 32.80 | 0.3280 | 0.0000 |
| `default` | `graph_100` | 2 | `dijkstra` | 0.2022 | 0.2365 | N/A | 79.40 | 0.7940 | 0.0000 |
| `default` | `graph_100` | 3 | `bidirectional_dijkstra` | 0.2151 | 0.3500 | N/A | 60.40 | 0.6040 | 0.0000 |
| `default` | `graph_100` | 4 | `a_star` | 0.2867 | 0.3640 | 0.4288 | 78.40 | 0.7840 | 0.0000 |
| `default` | `graph_100` | 5 | `weighted_a_star` | 0.3333 | 0.5043 | 0.0026 | 77.60 | 0.7760 | 0.0000 |
| `default` | `graph_100` | 6 | `bidirectional_a_star` | 0.8156 | 1.3713 | N/A | 170.80 | 1.7080 | -0.0000 |
| `default` | `graph_1000` | 1 | `a_star_alt` | 1.2538 | 2.6979 | 61.4766 | 152.40 | 0.1524 | 0.0000 |
| `default` | `graph_1000` | 2 | `dijkstra` | 1.4899 | 3.5555 | N/A | 411.00 | 0.4110 | 0.0000 |
| `default` | `graph_1000` | 3 | `weighted_a_star` | 2.0632 | 4.7447 | 0.0022 | 393.40 | 0.3934 | 0.0000 |
| `default` | `graph_1000` | 4 | `bidirectional_dijkstra` | 2.0656 | 4.6520 | N/A | 285.20 | 0.2852 | -0.0000 |
| `default` | `graph_1000` | 5 | `a_star` | 2.5745 | 7.9802 | 6.4599 | 396.80 | 0.3968 | 0.0000 |
| `default` | `graph_1000` | 6 | `bidirectional_a_star` | 7.1494 | 17.9449 | N/A | 1001.80 | 1.0018 | -0.0000 |
| `default` | `graph_1000_stress` | 1 | `a_star_alt` | 1.2193 | 3.2333 | 140.3787 | 71.00 | 0.0710 | 0.0000 |
| `default` | `graph_1000_stress` | 2 | `bidirectional_dijkstra` | 1.6310 | 4.6492 | N/A | 256.00 | 0.2560 | 0.0000 |
| `default` | `graph_1000_stress` | 3 | `dijkstra` | 1.7107 | 4.5109 | N/A | 358.60 | 0.3586 | 0.0000 |
| `default` | `graph_1000_stress` | 4 | `a_star` | 2.1493 | 6.0124 | 9.0533 | 332.00 | 0.3320 | 0.0000 |
| `default` | `graph_1000_stress` | 5 | `weighted_a_star` | 3.4313 | 12.0629 | 0.0021 | 323.60 | 0.3236 | 0.0000 |
| `default` | `graph_1000_stress` | 6 | `bidirectional_a_star` | 8.7216 | 19.9007 | N/A | 976.40 | 0.9764 | -0.0000 |
| `default` | `graph_5000` | 1 | `a_star_alt` | 5.4059 | 12.1309 | 448.2988 | 537.60 | 0.1075 | 0.0000 |
| `default` | `graph_5000` | 2 | `dijkstra` | 17.6475 | 23.8034 | N/A | 3740.80 | 0.7482 | 0.0000 |
| `default` | `graph_5000` | 3 | `a_star` | 22.1447 | 33.5167 | 28.3120 | 3664.00 | 0.7328 | 0.0000 |
| `default` | `graph_5000` | 4 | `weighted_a_star` | 22.2951 | 34.1816 | 0.0018 | 3648.20 | 0.7296 | 0.0000 |
| `default` | `graph_5000` | 5 | `bidirectional_dijkstra` | 23.7918 | 37.5084 | N/A | 3517.80 | 0.7036 | -0.0000 |
| `default` | `graph_5000` | 6 | `bidirectional_a_star` | 71.7341 | 94.7600 | N/A | 8728.40 | 1.7457 | -0.0000 |
| `seed43` | `graph_100` | 1 | `a_star_alt` | 0.1554 | 0.1956 | 4.7627 | 24.20 | 0.2420 | 0.0000 |
| `seed43` | `graph_100` | 2 | `dijkstra` | 0.1576 | 0.2047 | N/A | 71.80 | 0.7180 | 0.0000 |
| `seed43` | `graph_100` | 3 | `bidirectional_dijkstra` | 0.1632 | 0.2949 | N/A | 49.60 | 0.4960 | 0.0000 |
| `seed43` | `graph_100` | 4 | `a_star` | 0.2340 | 0.2992 | 0.4326 | 69.60 | 0.6960 | 0.0000 |
| `seed43` | `graph_100` | 5 | `weighted_a_star` | 0.2426 | 0.3259 | 0.0022 | 69.40 | 0.6940 | 0.0000 |
| `seed43` | `graph_100` | 6 | `bidirectional_a_star` | 0.7089 | 1.0609 | N/A | 158.80 | 1.5880 | -0.0000 |
| `seed43` | `graph_1000` | 1 | `a_star_alt` | 0.6364 | 1.2289 | 62.8303 | 86.40 | 0.0864 | 0.0000 |
| `seed43` | `graph_1000` | 2 | `dijkstra` | 1.0787 | 2.5150 | N/A | 301.80 | 0.3018 | 0.0000 |
| `seed43` | `graph_1000` | 3 | `a_star` | 1.3850 | 2.9397 | 5.3982 | 278.80 | 0.2788 | 0.0000 |
| `seed43` | `graph_1000` | 4 | `weighted_a_star` | 1.3908 | 2.9137 | 0.0029 | 272.60 | 0.2726 | 0.0000 |
| `seed43` | `graph_1000` | 5 | `bidirectional_dijkstra` | 2.0237 | 4.2520 | N/A | 334.80 | 0.3348 | 0.0000 |
| `seed43` | `graph_1000` | 6 | `bidirectional_a_star` | 6.8949 | 11.1808 | N/A | 1075.80 | 1.0758 | -0.0000 |
| `seed43` | `graph_1000_stress` | 1 | `a_star_alt` | 0.9943 | 3.8836 | 101.8199 | 89.20 | 0.0892 | 0.0000 |
| `seed43` | `graph_1000_stress` | 2 | `dijkstra` | 2.1451 | 5.2283 | N/A | 407.40 | 0.4074 | 0.0000 |
| `seed43` | `graph_1000_stress` | 3 | `weighted_a_star` | 2.5983 | 6.0735 | 0.0011 | 386.80 | 0.3868 | 0.0000 |
| `seed43` | `graph_1000_stress` | 4 | `a_star` | 2.6157 | 6.3920 | 7.7457 | 392.60 | 0.3926 | 0.0000 |
| `seed43` | `graph_1000_stress` | 5 | `bidirectional_dijkstra` | 2.6293 | 5.8293 | N/A | 392.80 | 0.3928 | -0.0000 |
| `seed43` | `graph_1000_stress` | 6 | `bidirectional_a_star` | 10.0362 | 17.6494 | N/A | 1192.40 | 1.1924 | -0.0000 |
| `seed43` | `graph_5000` | 1 | `a_star_alt` | 12.9834 | 30.1892 | 391.1340 | 1448.20 | 0.2896 | 0.0000 |
| `seed43` | `graph_5000` | 2 | `dijkstra` | 16.9241 | 21.9732 | N/A | 3774.40 | 0.7549 | 0.0000 |
| `seed43` | `graph_5000` | 3 | `bidirectional_dijkstra` | 22.1358 | 29.2713 | N/A | 3357.00 | 0.6714 | -0.0000 |
| `seed43` | `graph_5000` | 4 | `weighted_a_star` | 22.2995 | 31.0700 | 0.0014 | 3678.00 | 0.7356 | 0.0000 |
| `seed43` | `graph_5000` | 5 | `a_star` | 22.3706 | 34.0112 | 28.4886 | 3697.20 | 0.7394 | 0.0000 |
| `seed43` | `graph_5000` | 6 | `bidirectional_a_star` | 72.4582 | 85.7538 | N/A | 8761.40 | 1.7523 | -0.0000 |

## TDSP Problem

| Suite | Dataset | Rank | Algorithm | Mean runtime (ms) | Max runtime (ms) | Preprocess (ms) | Expanded nodes mean | Stress mean | Optimality gap mean |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| `default` | `graph_100` | 1 | `bidirectional_time_a_star` | 0.1692 | 0.3275 | 2.1831 | 45.60 | 0.4560 | N/A |
| `default` | `graph_100` | 2 | `dijkstra` | 0.1942 | 0.6413 | N/A | 77.80 | 0.7780 | N/A |
| `default` | `graph_100` | 3 | `dijkstra_contracted` | 0.2391 | 0.3526 | 0.9125 | 77.80 | 0.7780 | N/A |
| `default` | `graph_100` | 4 | `a_star` | 0.2637 | 0.3974 | 0.4288 | 75.00 | 0.7500 | N/A |
| `default` | `graph_100` | 5 | `weighted_a_star` | 0.2743 | 0.4042 | 0.0026 | 74.20 | 0.7420 | N/A |
| `default` | `graph_100` | 6 | `a_star_alt` | 0.2940 | 0.6451 | 4.6539 | 50.60 | 0.5060 | N/A |
| `default` | `graph_100` | 7 | `a_star_departure_alt` | 0.3711 | 0.5894 | 3.7445 | 50.60 | 0.5060 | N/A |
| `default` | `graph_100` | 8 | `a_star_active_alt` | 0.3750 | 0.6510 | 12.3520 | 55.40 | 0.5540 | N/A |
| `default` | `graph_100` | 9 | `a_star_contracted` | 0.4682 | 1.3141 | 0.0053 | 75.00 | 0.7500 | N/A |
| `default` | `graph_1000` | 1 | `bidirectional_time_a_star` | 0.6223 | 1.4167 | 24.4201 | 145.20 | 0.1452 | N/A |
| `default` | `graph_1000` | 2 | `dijkstra_contracted` | 1.4558 | 3.1952 | 9.0461 | 428.40 | 0.4284 | N/A |
| `default` | `graph_1000` | 3 | `a_star_alt` | 1.5087 | 3.3390 | 61.4766 | 229.00 | 0.2290 | N/A |
| `default` | `graph_1000` | 4 | `a_star_active_alt` | 1.5288 | 3.8827 | 148.7250 | 223.80 | 0.2238 | N/A |
| `default` | `graph_1000` | 5 | `a_star_departure_alt` | 1.6335 | 3.8770 | 35.7847 | 229.00 | 0.2290 | N/A |
| `default` | `graph_1000` | 6 | `dijkstra` | 1.9240 | 6.7181 | N/A | 428.40 | 0.4284 | N/A |
| `default` | `graph_1000` | 7 | `a_star_contracted` | 2.0901 | 5.7860 | 0.0018 | 408.40 | 0.4084 | N/A |
| `default` | `graph_1000` | 8 | `weighted_a_star` | 2.1102 | 5.0605 | 0.0022 | 403.80 | 0.4038 | N/A |
| `default` | `graph_1000` | 9 | `a_star` | 2.1257 | 5.4000 | 6.4599 | 408.40 | 0.4084 | N/A |
| `default` | `graph_1000_stress` | 1 | `bidirectional_time_a_star` | 0.8757 | 3.4000 | 41.0230 | 152.60 | 0.1526 | N/A |
| `default` | `graph_1000_stress` | 2 | `dijkstra` | 1.5443 | 4.9779 | N/A | 359.00 | 0.3590 | N/A |
| `default` | `graph_1000_stress` | 3 | `dijkstra_contracted` | 1.5654 | 4.5631 | 14.4419 | 359.00 | 0.3590 | N/A |
| `default` | `graph_1000_stress` | 4 | `a_star_active_alt` | 1.8396 | 6.2854 | 214.0793 | 212.60 | 0.2126 | N/A |
| `default` | `graph_1000_stress` | 5 | `a_star_departure_alt` | 1.8770 | 6.0695 | 56.5880 | 204.80 | 0.2048 | N/A |
| `default` | `graph_1000_stress` | 6 | `a_star` | 2.0447 | 6.5230 | 9.0533 | 337.60 | 0.3376 | N/A |
| `default` | `graph_1000_stress` | 7 | `a_star_contracted` | 2.0980 | 5.7494 | 0.0013 | 337.60 | 0.3376 | N/A |
| `default` | `graph_1000_stress` | 8 | `a_star_alt` | 2.7808 | 9.3211 | 140.3787 | 204.80 | 0.2048 | N/A |
| `default` | `graph_1000_stress` | 9 | `weighted_a_star` | 2.7822 | 9.5520 | 0.0021 | 332.40 | 0.3324 | N/A |
| `default` | `graph_5000` | 1 | `bidirectional_time_a_star` | 7.5916 | 17.3501 | 156.0355 | 1244.80 | 0.2490 | N/A |
| `default` | `graph_5000` | 2 | `a_star_active_alt` | 15.5173 | 29.0913 | 968.8013 | 1674.40 | 0.3349 | N/A |
| `default` | `graph_5000` | 3 | `a_star_departure_alt` | 16.5291 | 31.2094 | 232.6011 | 1677.20 | 0.3354 | N/A |
| `default` | `graph_5000` | 4 | `a_star_alt` | 16.6063 | 29.4061 | 448.2988 | 1677.20 | 0.3354 | N/A |
| `default` | `graph_5000` | 5 | `dijkstra_contracted` | 16.9955 | 22.6035 | 63.5269 | 3756.40 | 0.7513 | N/A |
| `default` | `graph_5000` | 6 | `dijkstra` | 17.7147 | 26.3754 | N/A | 3756.40 | 0.7513 | N/A |
| `default` | `graph_5000` | 7 | `a_star_contracted` | 22.3455 | 50.4860 | 0.0035 | 3638.20 | 0.7276 | N/A |
| `default` | `graph_5000` | 8 | `a_star` | 22.4203 | 36.9994 | 28.3120 | 3638.20 | 0.7276 | N/A |
| `default` | `graph_5000` | 9 | `weighted_a_star` | 22.6214 | 35.6565 | 0.0018 | 3608.40 | 0.7217 | N/A |
| `seed43` | `graph_100` | 1 | `bidirectional_time_a_star` | 0.1485 | 0.1930 | 1.6886 | 43.40 | 0.4340 | N/A |
| `seed43` | `graph_100` | 2 | `dijkstra` | 0.1652 | 0.2433 | N/A | 76.60 | 0.7660 | N/A |
| `seed43` | `graph_100` | 3 | `dijkstra_contracted` | 0.1714 | 0.2246 | 0.7567 | 76.60 | 0.7660 | N/A |
| `seed43` | `graph_100` | 4 | `weighted_a_star` | 0.2453 | 0.3654 | 0.0022 | 73.00 | 0.7300 | N/A |
| `seed43` | `graph_100` | 5 | `a_star` | 0.2458 | 0.3279 | 0.4326 | 74.00 | 0.7400 | N/A |
| `seed43` | `graph_100` | 6 | `a_star_alt` | 0.2517 | 0.3491 | 4.7627 | 46.80 | 0.4680 | N/A |
| `seed43` | `graph_100` | 7 | `a_star_contracted` | 0.2658 | 0.5821 | 0.0022 | 74.00 | 0.7400 | N/A |
| `seed43` | `graph_100` | 8 | `a_star_active_alt` | 0.2666 | 0.3298 | 10.1965 | 49.20 | 0.4920 | N/A |
| `seed43` | `graph_100` | 9 | `a_star_departure_alt` | 0.2748 | 0.3364 | 2.5896 | 46.80 | 0.4680 | N/A |
| `seed43` | `graph_1000` | 1 | `bidirectional_time_a_star` | 0.4831 | 0.9848 | 24.9950 | 115.00 | 0.1150 | N/A |
| `seed43` | `graph_1000` | 2 | `a_star_alt` | 1.0355 | 2.2193 | 62.8303 | 156.60 | 0.1566 | N/A |
| `seed43` | `graph_1000` | 3 | `a_star_departure_alt` | 1.0785 | 2.3893 | 33.9432 | 156.60 | 0.1566 | N/A |
| `seed43` | `graph_1000` | 4 | `a_star_active_alt` | 1.0953 | 3.0694 | 147.7899 | 155.60 | 0.1556 | N/A |
| `seed43` | `graph_1000` | 5 | `dijkstra` | 1.1297 | 2.9650 | N/A | 338.60 | 0.3386 | N/A |
| `seed43` | `graph_1000` | 6 | `dijkstra_contracted` | 1.1478 | 3.0479 | 9.6979 | 338.60 | 0.3386 | N/A |
| `seed43` | `graph_1000` | 7 | `a_star` | 1.5081 | 4.1052 | 5.3982 | 315.00 | 0.3150 | N/A |
| `seed43` | `graph_1000` | 8 | `weighted_a_star` | 1.5297 | 4.3248 | 0.0029 | 309.00 | 0.3090 | N/A |
| `seed43` | `graph_1000` | 9 | `a_star_contracted` | 1.5784 | 4.0735 | 0.0023 | 315.00 | 0.3150 | N/A |
| `seed43` | `graph_1000_stress` | 1 | `bidirectional_time_a_star` | 1.1153 | 3.4061 | 40.9633 | 190.00 | 0.1900 | N/A |
| `seed43` | `graph_1000_stress` | 2 | `dijkstra` | 1.7411 | 4.2520 | N/A | 398.60 | 0.3986 | N/A |
| `seed43` | `graph_1000_stress` | 3 | `dijkstra_contracted` | 1.7415 | 4.4332 | 13.8255 | 398.60 | 0.3986 | N/A |
| `seed43` | `graph_1000_stress` | 4 | `a_star_active_alt` | 1.9546 | 4.8714 | 219.8966 | 231.00 | 0.2310 | N/A |
| `seed43` | `graph_1000_stress` | 5 | `a_star_alt` | 2.0363 | 5.6251 | 101.8199 | 227.60 | 0.2276 | N/A |
| `seed43` | `graph_1000_stress` | 6 | `a_star_departure_alt` | 2.1094 | 5.4135 | 52.8998 | 227.60 | 0.2276 | N/A |
| `seed43` | `graph_1000_stress` | 7 | `a_star` | 2.3110 | 5.4372 | 7.7457 | 380.20 | 0.3802 | N/A |
| `seed43` | `graph_1000_stress` | 8 | `a_star_contracted` | 2.4001 | 5.3741 | 0.0012 | 380.20 | 0.3802 | N/A |
| `seed43` | `graph_1000_stress` | 9 | `weighted_a_star` | 2.4448 | 5.6682 | 0.0011 | 374.80 | 0.3748 | N/A |
| `seed43` | `graph_5000` | 1 | `bidirectional_time_a_star` | 8.1056 | 24.5257 | 155.0587 | 1260.80 | 0.2522 | N/A |
| `seed43` | `graph_5000` | 2 | `dijkstra` | 17.1676 | 25.5337 | N/A | 3725.00 | 0.7450 | N/A |
| `seed43` | `graph_5000` | 3 | `dijkstra_contracted` | 17.2152 | 23.0101 | 61.7817 | 3725.00 | 0.7450 | N/A |
| `seed43` | `graph_5000` | 4 | `a_star_alt` | 18.4145 | 41.3413 | 391.1340 | 2058.20 | 0.4116 | N/A |
| `seed43` | `graph_5000` | 5 | `a_star_active_alt` | 18.8831 | 41.3870 | 987.0849 | 2097.40 | 0.4195 | N/A |
| `seed43` | `graph_5000` | 6 | `a_star_departure_alt` | 19.0268 | 42.2017 | 209.1323 | 2058.20 | 0.4116 | N/A |
| `seed43` | `graph_5000` | 7 | `a_star` | 22.4166 | 33.8283 | 28.4886 | 3617.00 | 0.7234 | N/A |
| `seed43` | `graph_5000` | 8 | `weighted_a_star` | 22.8086 | 33.1890 | 0.0014 | 3590.00 | 0.7180 | N/A |
| `seed43` | `graph_5000` | 9 | `a_star_contracted` | 22.8755 | 45.5095 | 0.0180 | 3617.00 | 0.7234 | N/A |

## Quick Ranking Takeaways

- Distance winner in every archived dataset: `a_star_alt`
- TDSP winner in every archived dataset: `bidirectional_time_a_star`
- The largest preprocessing costs come from ALT-based methods, especially `a_star_active_alt` and `a_star_alt` on `graph_5000`
- Heavy preprocessing only makes sense when the same graph is queried repeatedly; otherwise the lighter methods are easier to justify

