"""Backward-compatible import shim for legacy misspelled package name."""

from evaluation.benchmark import benchmark_dijkstra, write_runtime_csv

__all__ = ["benchmark_dijkstra", "write_runtime_csv"]
