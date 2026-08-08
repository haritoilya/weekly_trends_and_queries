#!/usr/bin/env python3
"""Deterministic opportunity scoring. Usage: python3 scripts/score.py clusters.json
Reads a JSON array of cluster objects from a file (not argv, to save tokens on large sets),
prints the same array sorted by opportunity_score, each with the field added."""
import json, sys

def score(c):
    values = list(c["region_scores"].values()) or [0]
    avg = sum(values) / len(values) if values else 0
    arbitrage_index = (max(values) / avg) if avg else 0
    rising_norm = min(1.0, c["growth_pct"] / 300.0)
    arb_norm = min(1.0, arbitrage_index / 5.0)
    cluster_size_norm = min(1.0, c.get("cluster_size", 1) / 10.0)
    return round(
        0.35 * rising_norm + 0.25 * arb_norm + 0.25 * c["serp_open"] + 0.15 * cluster_size_norm,
        3,
    )

path = sys.argv[1]
clusters = json.load(open(path))
for c in clusters:
    c["opportunity_score"] = score(c)
clusters.sort(key=lambda x: x["opportunity_score"], reverse=True)
print(json.dumps(clusters, ensure_ascii=False))
