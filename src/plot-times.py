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

    groups = (pd
              .read_csv(sys.stdin)
              .groupby('experiment', sort=False, dropna=False))

    nrows = groups.ngroups
    (fig, axes) = plt.subplots(nrows=nrows, sharex=True)
    (width, height) = fig.get_size_inches()
    fig.set_size_inches(width * 1.2, height * nrows)

    first = 1
    hue = 'response'
    kwargs = {
        'x': 'seconds',
        'hue': hue,
    }
    sns.set_palette('colorblind')
    for (i, (ax, (e, df))) in enumerate(zip(axes, groups), first):
        sns.ecdfplot(
            data=df,
            ax=ax,
            **kwargs,
        )

        ax.set_xlabel('Duration (sec)' if i == nrows else '')
        ax.set_title(
            label=e,
            loc='right',
            fontdict={
                'fontsize': 'medium',
                'fontweight': 'bold',
            },
        )

        ax.grid(axis='both', which='major', alpha=0.3)
        ax.grid(axis='both', which='minor', alpha=0.25, linestyle='dotted')

        ax.xaxis.set_major_locator(MultipleLocator(base=2))
        ax.xaxis.set_minor_locator(MultipleLocator())
        ax.yaxis.set_major_locator(MultipleLocator(base=0.1))
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        if args.cutoff is not None:
            ax.set_xlim(0, args.cutoff)

        view = (df
                .filter(items=kwargs.values())
                .groupby(hue)
                .mean())
        for l in lines(ax):
            x = view.loc[l.name].item()
            ax.axvline(
                x=x,
                linestyle='dashed',
                color=l.color,
                alpha=0.45,
            )
        if i == first:
            sns.move_legend(ax, 'best', title=None)
        else:
            ax.get_legend().remove()

    plt.savefig(args.output, bbox_inches='tight')
