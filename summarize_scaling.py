"""
Aggregate BFS scaling timings while ignoring graph generator and topology.

The output contains one row per part-count, size, and density profile. Mean
times for each parallel process count and each distributed worker count are
written to separate, dynamically generated columns.

Examples:
    python summarize_scaling.py
    python summarize_scaling.py --input-dir results/scaling
    python summarize_scaling.py --include-incorrect
"""

import argparse
import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = ROOT_DIR / "results" / "scaling"
DEFAULT_OUTPUT_PATH = DEFAULT_INPUT_DIR / "scaling_statistics.csv"


@dataclass(frozen=True)
class Source:
    path: Path
    family: str
    variant_time_column: str
    rows: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class ProfileKey:
    parts: str
    size: str
    density: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate scaling benchmark times by part-count, size, and "
            "density profiles."
        ),
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory containing scaling CSV files (default: {DEFAULT_INPUT_DIR}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    parser.add_argument(
        "--include-incorrect",
        action="store_true",
        help="Include rows whose correctness flag is not true.",
    )
    parser.add_argument(
        "--allow-missing-components",
        action="store_true",
        help=(
            "Write an empty component count when it cannot be inferred from "
            "distributed results instead of failing."
        ),
    )
    return parser.parse_args()


def read_source(path: Path) -> Source | None:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = set(reader.fieldnames or ())

        if {"record_type", "seq_time_s", "par_time_s"} <= fieldnames:
            family = "parallel"
            variant_time_column = "par_time_s"
        elif {"record_type", "seq_time_s", "dist_time_s"} <= fieldnames:
            family = "distributed"
            variant_time_column = "dist_time_s"
        else:
            return None

        rows = tuple(row for row in reader if row.get("record_type") == "run")

    if not rows:
        return None
    return Source(path, family, variant_time_column, rows)


def discover_sources(input_dir: Path, output_path: Path) -> list[Source]:
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    output_resolved = output_path.resolve()
    sources = []
    for path in sorted(input_dir.glob("*.csv")):
        if path.resolve() == output_resolved:
            continue
        source = read_source(path)
        if source is not None:
            sources.append(source)

    if not sources:
        raise ValueError(f"No scaling measurement CSV files found in {input_dir}")
    return sources


def graph_key(graph_path: str) -> str:
    normalized = graph_path.strip().replace("\\", "/").lower()
    marker = "/graphs/"
    if marker in normalized:
        return normalized.split(marker, 1)[1]
    return normalized


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def build_component_index(sources: list[Source]) -> dict[str, int]:
    components_by_graph = {}
    for source in sources:
        for row in source.rows:
            raw_components = row.get("components", "").strip()
            if not raw_components:
                continue

            key = graph_key(row["graph_path"])
            components = int(raw_components)
            previous = components_by_graph.setdefault(key, components)
            if previous != components:
                raise ValueError(
                    f"Conflicting component counts for {row['graph_path']}: "
                    f"{previous} and {components}"
                )
    return components_by_graph


def graph_profile(graph_path: str) -> ProfileKey:
    path_parts = graph_key(graph_path).split("/")
    filename = Path(path_parts[-1]).stem
    size = filename.rsplit("_", 1)[0]

    if path_parts[0] == "connected":
        parts = "one"
        density = "grid" if len(path_parts) == 3 else path_parts[-2]
    elif path_parts[0] == "inconsistent":
        parts = path_parts[2]
        density = "grid" if len(path_parts) == 4 else path_parts[-2]
    else:
        raise ValueError(f"Unknown graph path layout: {graph_path}")

    if parts == "medium":
        parts = "some"
    return ProfileKey(parts=parts, size=size, density=density)


def profile_label(key: ProfileKey) -> str:
    part_text = "one part" if key.parts == "one" else f"{key.parts} parts"
    return f"{part_text} {key.size} & {key.density}"


def graph_density(nodes: int, edges: int) -> float:
    if nodes < 2:
        return 0.0
    # The files store adjacency entries. For an undirected graph each edge is
    # stored twice, so this is also the standard undirected graph density.
    return edges / (nodes * (nodes - 1))


def add_measurement(
    timings: dict[ProfileKey, dict[int, dict[str, list[float]]]],
    key: ProfileKey,
    executors: int,
    algorithm: str,
    value: str,
) -> None:
    timings[key][executors][algorithm].append(float(value))


def aggregate(
    sources: list[Source],
    include_incorrect: bool,
    allow_missing_components: bool,
) -> tuple[
    dict[ProfileKey, dict[int, dict[str, list[float]]]],
    dict[ProfileKey, dict[int, dict[str, list[float]]]],
    dict[ProfileKey, dict[str, tuple[int, int, int | None]]],
    int,
]:
    components_by_graph = build_component_index(sources)
    parallel_timings = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    distributed_timings = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    graph_metadata = defaultdict(dict)
    skipped_incorrect = 0

    for source in sources:
        for row in source.rows:
            if not include_incorrect and not parse_bool(row.get("correct", "")):
                skipped_incorrect += 1
                continue

            nodes = int(row["nodes"])
            edges = int(row["edges"])
            executors = int(row["workers"])
            graph = graph_key(row["graph_path"])
            raw_components = row.get("components", "").strip()
            components = (
                int(raw_components)
                if raw_components
                else components_by_graph.get(graph)
            )
            if components is None and not allow_missing_components:
                raise ValueError(
                    "Missing component count for "
                    f"{row['graph_path']}. Add matching distributed results or "
                    "use --allow-missing-components."
                )

            key = graph_profile(row["graph_path"])
            metadata = (nodes, edges, components)
            previous_metadata = graph_metadata[key].setdefault(graph, metadata)
            if previous_metadata != metadata:
                raise ValueError(
                    f"Conflicting metadata for {row['graph_path']}: "
                    f"{previous_metadata} and {metadata}"
                )
            timings = (
                parallel_timings
                if source.family == "parallel"
                else distributed_timings
            )

            add_measurement(
                timings,
                key,
                executors,
                "sequential",
                row["seq_time_s"],
            )
            add_measurement(
                timings,
                key,
                executors,
                source.family,
                row[source.variant_time_column],
            )

    return (
        parallel_timings,
        distributed_timings,
        graph_metadata,
        skipped_incorrect,
    )


def graph_sort_key(key: ProfileKey) -> tuple:
    size_order = {"tiny": 0, "small": 1, "medium": 2, "large": 3, "huge": 4}
    density_order = {"sparse": 0, "medium": 1, "dense": 2, "grid": 3}
    parts_order = {"one": 0, "few": 1, "some": 2, "many": 3}
    return (
        parts_order[key.parts],
        size_order[key.size],
        density_order[key.density],
    )


def mean_or_empty(values: list[float]) -> float | str:
    return statistics.fmean(values) if values else ""


def speedup(sequential_time: float | str, variant_time: float | str) -> float | str:
    if sequential_time == "" or variant_time == "":
        return ""
    return sequential_time / variant_time if variant_time > 0 else float("inf")


def mean_number(values: list[int]) -> int | float | str:
    if not values:
        return ""
    mean = statistics.fmean(values)
    return int(mean) if mean.is_integer() else mean


def write_summary(
    output_path: Path,
    parallel_timings: dict[
        ProfileKey,
        dict[int, dict[str, list[float]]],
    ],
    distributed_timings: dict[
        ProfileKey,
        dict[int, dict[str, list[float]]],
    ],
    graph_metadata: dict[
        ProfileKey,
        dict[str, tuple[int, int, int | None]],
    ],
) -> int:
    process_counts = sorted({
        processes
        for executor_timings in parallel_timings.values()
        for processes in executor_timings
    })
    worker_counts = sorted({
        workers
        for executor_timings in distributed_timings.values()
        for workers in executor_timings
    })
    fields = [
        "graph_label",
        "nodes",
        "components",
        "sequential_mean_time_s",
    ]
    for processes in process_counts:
        fields.extend([
            f"parallel_{processes}_processes_mean_time_s",
            f"parallel_{processes}_processes_speedup",
        ])
    for workers in worker_counts:
        fields.extend([
            f"distributed_{workers}_workers_mean_time_s",
            f"distributed_{workers}_workers_speedup",
        ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        rows_written = 0
        graph_keys = set(parallel_timings) & set(distributed_timings)
        for key in sorted(graph_keys, key=graph_sort_key):
            metadata = list(graph_metadata[key].values())
            nodes = [item[0] for item in metadata]
            components = [
                item[2] for item in metadata if item[2] is not None
            ]
            sequential_values = []
            for values_by_algorithm in parallel_timings[key].values():
                sequential_values.extend(values_by_algorithm["sequential"])
            for values_by_algorithm in distributed_timings[key].values():
                sequential_values.extend(values_by_algorithm["sequential"])

            sequential_mean = mean_or_empty(sequential_values)
            row = {
                "graph_label": profile_label(key),
                "nodes": mean_number(nodes),
                "components": mean_number(components),
                "sequential_mean_time_s": sequential_mean,
            }
            for processes in process_counts:
                mean_time = mean_or_empty(
                    parallel_timings[key][processes]["parallel"]
                )
                row[f"parallel_{processes}_processes_mean_time_s"] = mean_time
                row[f"parallel_{processes}_processes_speedup"] = speedup(
                    sequential_mean,
                    mean_time,
                )
            for workers in worker_counts:
                mean_time = mean_or_empty(
                    distributed_timings[key][workers]["distributed"]
                )
                row[f"distributed_{workers}_workers_mean_time_s"] = mean_time
                row[f"distributed_{workers}_workers_speedup"] = speedup(
                    sequential_mean,
                    mean_time,
                )

            writer.writerow(row)
            rows_written += 1
    return rows_written


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_path = args.output.resolve()

    sources = discover_sources(input_dir, output_path)
    (
        parallel_timings,
        distributed_timings,
        graph_metadata,
        skipped_incorrect,
    ) = aggregate(
        sources,
        include_incorrect=args.include_incorrect,
        allow_missing_components=args.allow_missing_components,
    )
    rows_written = write_summary(
        output_path,
        parallel_timings,
        distributed_timings,
        graph_metadata,
    )

    measurement_count = sum(
        len(values)
        for family_timings in (parallel_timings, distributed_timings)
        for executor_timings in family_timings.values()
        for values_by_algorithm in executor_timings.values()
        for values in values_by_algorithm.values()
    )
    print(f"Read {len(sources)} measurement files from: {input_dir}")
    print(f"Wrote {rows_written} aggregate rows to: {output_path}")
    print(f"Aggregated {measurement_count} algorithm measurements.")
    if skipped_incorrect:
        print(f"Skipped {skipped_incorrect} incorrect run rows.")


if __name__ == "__main__":
    main()
