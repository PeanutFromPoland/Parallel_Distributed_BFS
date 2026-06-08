import cProfile
import os
import pstats

import worker


PROFILE_DIR = os.environ.get("PROFILE_DIR", "/app/results/profiles")
NODE_NAME = os.environ.get("NODE_NAME", os.environ.get("HOSTNAME", "worker"))


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

    profiler = cProfile.Profile()
    try:
        profiler.enable()
        worker.main()
    finally:
        profiler.disable()
        profiler.dump_stats(profile_path)
        with open(profile_txt_path, "w", encoding="utf-8") as file:
            stats = pstats.Stats(profiler, stream=file)
            stats.sort_stats("cumulative").print_stats(60)
        print(f"\nProfil cProfile zapisano w: {profile_path}", flush=True)
        print(f"Podsumowanie profilu zapisano w: {profile_txt_path}", flush=True)


if __name__ == "__main__":
    main()
