import sys
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--cutoff', type=float)
    arguments.add_argument('--output', type=Path)
    args = arguments.parse_args()

    x = 'duration'
    df = pd.read_csv(sys.stdin)
    ax = sns.ecdfplot(x=x, data=df)

    ax.set_xlabel('Duration (sec)')

    ax.grid(axis='both', which='major', alpha=0.3)
    ax.grid(axis='y', which='minor', alpha=0.25, linestyle='dotted')

    ax.xaxis.set_major_locator(MultipleLocator(base=2))
    ax.yaxis.set_major_locator(MultipleLocator(base=0.1))
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.axvline(
        x=df[x].mean(),
        linestyle='dashed',
        color='red',
        alpha=0.3,
    )
    if args.cutoff is not None:
        ax.set_xlim(0, args.cutoff)

    plt.savefig(args.output, bbox_inches='tight')
