import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse


def parse_args() -> tuple[int, int, int, int]:
    parser = argparse.ArgumentParser(description='Merge sort with threads')
    parser.add_argument('--use_process', action='store_true', help='Use process instead of threads')
    parser.add_argument('--sort_type', type=str, help='Type of sort (bubble, python)', default='python')
    args = parser.parse_args()    

    return args

args = parse_args()
print(args)
file = f"{'process' if args.use_process else 'threads'}_{args.sort_type}_report.csv"
df = pd.read_csv(file, sep=";")
df  = df.drop(columns=["time"])
df = df.groupby(["n", "array_size"]).mean().reset_index()
df.plot(x="n", y="time_elapsed", marker="o", legend=False)

sort_type = "Bubble sort" if args.sort_type == "bubble" else "Timsort sort"
n_type = "Process" if args.use_process else "Thread"

plt.title(f'{sort_type} perfomance with {n_type} x time')
plt.xlabel(f'Number of {n_type}')
plt.ylabel('Time in ms')

plt.savefig(f"analysis/{n_type}_{args.sort_type}.png")