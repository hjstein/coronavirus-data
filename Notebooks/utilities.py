from pandas import plotting


def plot_multi(data, cols=None, spacing=.1, **kwargs):
    '''Plot columns, each with a separate Y axis
    '''

    if cols is None:
        cols = data.columns
    if len(cols) == 0:
        return
    colors = getattr(getattr(plotting, '_matplotlib').style,
                     '_get_standard_colors')(num_colors=len(cols))

    # First axis
    ax = data.loc[:, cols[0]].plot(label=cols[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols[0])
    lines, labels = ax.get_legend_handles_labels()

    for n in range(1, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.loc[:, cols[n]].plot(ax=ax_new,
                                  label=cols[n],
                                  color=colors[n % len(colors)],
                                  **kwargs)
        ax_new.set_ylabel(ylabel=cols[n])

        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

        ax_new.yaxis.grid(False, which='both')

    ax.legend(lines, labels, loc=0)

    return ax
