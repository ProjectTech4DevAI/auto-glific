import sys
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--cutoff', type=float)
    arguments.add_argument('--output', type=Path)
    args = arguments.parse_args()

    x = 'duration'
    df = pd.read_csv(sys.stdin)
    sns.ecdfplot(x=x, data=df)

    plt.grid(
        visible=True,
        axis='both',
        alpha=0.25,
    )
    plt.xlabel('Duration (sec)')
    plt.axvline(
        x=df[x].mean(),
        linestyle='dashed',
        color='red',
        alpha=0.3,
    )
    if args.cutoff is not None:
        plt.xlim(0, args.cutoff)

    plt.savefig(args.output, bbox_inches='tight')
