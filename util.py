"""MLT: Utility code."""

import os
import pandas as pd
import matplotlib.pyplot as plt
import urllib2

def update_data(symbols=['SPY']):
    if type(symbols) is not list:
        symbols = list(symbols)
    if 'SPY' not in symbols:
        symbols = symbols + ['SPY']
    for symbol in symbols:
        data_file=urllib2.urlopen("http://chart.finance.yahoo.com/table.csv?s=%s&a=0&b=2&c=1980&d=2&e=30&f=2017&g=d&ignore=.csv"%symbol)
        f = open(symbol_to_path(symbol),'w')
        f.write(data_file.read())
        f.close()
        data_file.close()

def symbol_to_path(symbol, base_dir=os.path.join(".", "data"), ):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))

def get_data(symbols, dates, addSPY=True, colname = 'Adj Close'):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    if addSPY and 'SPY' not in symbols:  # add SPY for reference, if absent
        symbols = ['SPY'] + symbols

    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', colname], na_values=['nan'])
        df_temp = df_temp.rename(columns={colname: symbol})
        df = df.join(df_temp)
        if symbol == 'SPY':  # drop dates SPY did not trade
            df = df.dropna(subset=["SPY"])

    return df

def plot_data(df, title="Stock prices", xlabel="Date", ylabel="Price"):
    """Plot stock prices with a custom title and meaningful axis labels."""
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.show()
