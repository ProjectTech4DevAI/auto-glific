import sys
import operator as op
import itertools as it
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from mylib import Logger

@dataclass
class PlotLine:
    name: str
    color: tuple

class LayoutManager:
    def __init__(self, nrows):
        self.nrows = nrows
        (self.fig, self.axes) = plt.subplots(nrows=self.nrows, sharex=True)

    def __iter__(self):
        if self.nrows > 1:
            yield from self.axes
        else:
            yield self.axes

    def expand(self, width, height):
        iterable = zip((width, height), self.fig.get_size_inches())
        args = it.starmap(op.mul, iterable)
        self.fig.set_size_inches(*args)

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
    layout = LayoutManager(nrows)
    layout.expand(1.2, nrows)

    first = 1
    hue = 'response'
    kwargs = {
        'x': 'seconds',
        'hue': hue,
    }

    for (i, (ax, (e, df))) in enumerate(zip(layout, groups), first):
        Logger.info(e)

        sns.ecdfplot(
            data=df,
            ax=ax,
            **kwargs,
        )

        ax.set_xlabel('Duration (sec)' if i == nrows else '')
        ax.set_title(
            label=f'{e} (N={len(df)})',
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
                alpha=0.55,
            )
        if i == first:
            sns.move_legend(ax, 'best', title=None)
        else:
            ax.get_legend().remove()

    plt.savefig(args.output, bbox_inches='tight')
