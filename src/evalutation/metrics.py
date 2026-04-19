"""Backward-compatible import shim for legacy misspelled package name."""

from evaluation.metrics import (
    build_path_report,
    path_total_distance,
    path_total_travel_time,
)

__all__ = ["path_total_distance", "path_total_travel_time", "build_path_report"]
