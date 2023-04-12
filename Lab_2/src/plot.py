import matplotlib.pyplot as plt
import pathlib as pl
import pandas as pd

def plot_all_models(path):
    path = pl.Path(path)
    files = path.glob("*.csv")

    axis = []
    for file in files:
        df = pd.read_csv(file)
        plt.plot(df['accuracy'], label=file.stem)
        plt.ylim(0.9, 1)
    
    #plt.legend(axis, [file.stem for file in files])

    plt.xlabel("Rounds/Epochs")
    plt.ylabel("Accuracy")
    plt.title("Accuracy per round/epoch for each model")
    plt.legend(loc="lower right")
    plt.savefig(f"results/accuracy.png")

