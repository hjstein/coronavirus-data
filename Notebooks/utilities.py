import pandas as pd
from matplotlib import pyplot as plt

wave = {
    1: {"start": "2020-01-01",
        "end": "2020-07-01",
        "peakStart": "2020-03-09",
        "peakEnd": "2020-05-15"},
    2: {"start": "2020-09-01",
        "end": "2021-07-01"},
    3: {"start": "2021-07-01",
        "end": "2021-11-01",
        "name": "Delta"},
    4: {"start": "2021-11-01",
        "end": "2022-03-28",
        "name": "Omicron",
        "peakStart": "2021-12-01",
        "peakEnd": "2022-03-01"},
    5: {"start": "2022-03-01",
        "end": "2023-12-31",
        "name": "Omicron BA.2"}}

old_wave_ids = {"one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5}

count_cols = ["NEW_COVID_CASE_COUNT",
              "HOSPITALIZED_COUNT",
              "DEATH_COUNT"]

rolling_avg_cols = ["Cases/day, 7 day avg",
                    "Hospitalized/day, 7 day avg",
                    "Deaths/day, 7 day avg"]

aggregate_cols = ["Total cases",
                  "Total hospitalized",
                  "Total deaths"]


def load_data(file="../trends/data-by-day.csv"):
    '''Load case data'''
    dat = pd.read_csv("../trends/data-by-day.csv")
    dat.rename(columns={"CASE_COUNT": "NEW_COVID_CASE_COUNT",
                        "date_of_interest": "DATE_OF_INTEREST"},
               inplace=True)
    dat["DATE_OF_INTEREST"] = pd.to_datetime(dat["DATE_OF_INTEREST"])
    dat = dat.set_index("DATE_OF_INTEREST")

    return dat


def add_averages(dat,
                 in_cols=count_cols,
                 out_cols=rolling_avg_cols,
                 window_size="7D"):
    '''Add rolling averages for specified columns
    '''

    for incol, outcol in zip(in_cols, out_cols):
        dat[outcol] = dat[incol].rolling(window=window_size).mean()

    return dat


def add_aggregates(dat,
                   in_cols=count_cols,
                   out_cols=aggregate_cols):
    '''Add aggregate totals for specified columns
    '''

    for incol, outcol in zip(in_cols, out_cols):
        dat[outcol] = dat[incol].cumsum()

    return dat


def get_wave_id(waveId):
    '''Get new wave id.  Convert to new if old is supplied
    '''
    w = old_wave_ids.get(waveId)
    if w is None:
        w = waveId

    return w


def get_wave(waveId, peak=False):
    '''Get start and end of specified wave
    '''

    w = get_wave_id(waveId)

    if peak:
        return wave[w]["peakStart"], wave[w]["peakEnd"]
    else:
        return wave[w]["start"], wave[w]["end"]


def get_wave_name(waveId):
    '''Get name of specified wave
    '''

    return wave[get_wave_id(waveId)].get("name")


def get_range(df, start, end):
    return df[(df.index >= start) & (df.index < end)]


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


def calc_rate_std(dat, start, end, columns, denom):
    """Compute std rates for data with shifts
    """
    rng = range(start, end)
    newcols = []
    for col in columns:
        newcols.append(f"{col}/{denom}")

    stds = []
    for shift in rng:
        ratios = pd.DataFrame()
        for col, newcol in zip(columns, newcols):
            ratios[newcol] = dat[col]/dat[denom].shift(shift)

        stats = ratios[newcols].describe()

        stds.append(stats.loc["std"].values)

    df = pd.DataFrame(columns=newcols, data=stds)
    df["Shift"] = rng

    df.set_index("Shift", inplace=True)

    return df
