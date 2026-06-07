from main import main
import multiprocessing as mp
import cProfile

if __name__ == "__main__":
    mp.freeze_support()
    cProfile.run(main())