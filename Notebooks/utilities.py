from pandas import plotting
from matplotlib import pyplot as plt


def plot_multi(data, cols=None, spacing=.1, **kwargs):
    '''Plot columns, each with a separate Y axis
    '''

    if cols is None:
        cols = data.columns
    if len(cols) == 0:
        return
    # colors = getattr(getattr(plotting, '_matplotlib').style,
    #                  '_get_standard_colors')(num_colors=len(cols))

    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    # First axis
    color = colors[0]
    ax = data.loc[:, cols[0]].plot(label=cols[0], color=color, **kwargs)
    ax.set_ylabel(ylabel=cols[0], color=color)
    ax.tick_params(axis="y", labelcolor=color)
    lines, labels = ax.get_legend_handles_labels()

    for n in range(1, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        color = colors[n % len(colors)]
        data.loc[:, cols[n]].plot(ax=ax_new,
                                  label=cols[n],
                                  color=color,
                                  **kwargs)
        ax_new.set_ylabel(ylabel=cols[n], color=color)
        ax_new.tick_params(axis="y", labelcolor=color)

        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

        ax_new.yaxis.grid(False, which='both')

    ax.legend(lines, labels, loc=0)

    return ax
