import cProfile
import os
import pstats

import coordinator


DEFAULT_GRAPH_PATH = "/app/graphs/inconsistent/bb_bb/many/sparse/huge_001.txt"
PROFILE_DIR = os.environ.get("PROFILE_DIR", "/app/results/profiles")
NODE_NAME = os.environ.get("NODE_NAME", "coordinator")


def _resolve_path(path, base_dir):
    if os.path.isabs(path):
        return path
    return os.path.join(base_dir, path)


def _selected_graph_files(base_dir):
    graph_path = _resolve_path(
        os.environ.get("PROFILE_GRAPH_PATH", DEFAULT_GRAPH_PATH),
        base_dir,
    )
    expected_path = _resolve_path(
        os.environ.get("PROFILE_EXPECTED_PATH", graph_path[:-4] + "_expected.txt"),
        base_dir,
    )
    label = os.environ.get(
        "PROFILE_GRAPH_LABEL",
        f"[Profil] {os.path.relpath(graph_path, base_dir)}",
    )

    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Nie znaleziono grafu do profilowania: {graph_path}")
    if not os.path.exists(expected_path):
        raise FileNotFoundError(
            f"Nie znaleziono pliku expected dla profilowania: {expected_path}"
        )

    return [(graph_path, expected_path, label)]


def main():
    os.makedirs(PROFILE_DIR, exist_ok=True)
    profile_path = os.environ.get(
        "PROFILE_PATH",
        os.path.join(PROFILE_DIR, f"{NODE_NAME}.prof"),
    )
    profile_txt_path = os.environ.get(
        "PROFILE_TXT_PATH",
        os.path.join(PROFILE_DIR, f"{NODE_NAME}.txt"),
    )

    coordinator.collect_graph_files = _selected_graph_files

    profiler = cProfile.Profile()
    try:
        profiler.enable()
        coordinator.main()
    finally:
        profiler.disable()
        profiler.dump_stats(profile_path)
        with open(profile_txt_path, "w", encoding="utf-8") as file:
            stats = pstats.Stats(profiler, stream=file)
            stats.sort_stats("cumulative").print_stats(60)
        print(f"\n  Profil cProfile zapisano w: {profile_path}", flush=True)
        print(f"  Podsumowanie profilu zapisano w: {profile_txt_path}", flush=True)


if __name__ == "__main__":
    main()
