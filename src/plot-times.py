import sys
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

@dataclass
class PlotLine:
    name: str
    color: tuple

def lines(ax):
    legend = ax.get_legend()
    for (t, l) in zip(legend.get_texts(), legend.get_lines()):
        yield PlotLine(t.get_text(), l.get_color())

if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--cutoff', type=float)
    arguments.add_argument('--output', type=Path)
    args = arguments.parse_args()

    hue = 'response'
    df = pd.read_csv(sys.stdin)

    fig = plt.gcf()
    (width, height) = fig.get_size_inches()
    fig.set_size_inches(width * 1.5, height)

    sns.set_palette('colorblind')
    ax = sns.ecdfplot(
        x='seconds',
        hue=hue,
        data=df,
    )

    ax.set_xlabel('Duration (sec)')

    ax.grid(axis='both', which='major', alpha=0.3)
    ax.grid(axis='both', which='minor', alpha=0.25, linestyle='dotted')

    ax.xaxis.set_major_locator(MultipleLocator(base=2))
    ax.xaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_major_locator(MultipleLocator(base=0.1))
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    if args.cutoff is not None:
        ax.set_xlim(0, args.cutoff)

    view = df.groupby(hue).mean()
    for l in lines(ax):
        x = view.loc[l.name].item()
        ax.axvline(
            x=x,
            linestyle='dashed',
            color=l.color,
            alpha=0.45,
        )

    plt.savefig(args.output, bbox_inches='tight')
