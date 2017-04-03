"""MC1-P1: Analyze a portfolio."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from util import get_data, plot_data
import scipy.optimize as spo

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def assess_portfolio(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
    syms = ['GOOG','AAPL','GLD','XOM'], \
    allocs=[0.1,0.2,0.3,0.4], \
    sv=1000000, rfr=0.0, sf=252.0, \
    gen_plot=False):

    #assert sum(allocs) == 1.0
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value
    normed = prices /prices.ix[0]
    alloced = normed * allocs
    pos_vals = alloced * sv
    port_val = pos_vals.sum(axis=1)

    daily_returns = port_val.copy()
    daily_returns[1:] = (port_val[1:] / port_val[:-1].values) -1
    daily_returns = daily_returns[1:]

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cr = (port_val[-1]/port_val[0])-1
    adr = daily_returns.mean()
    sddr = daily_returns.std()
    sr = np.sqrt(sf) * (adr -  rfr) /sddr


    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        df_temp = pd.concat([port_val/port_val.ix[0], prices_SPY/prices_SPY.ix[0]], keys=['Portfolio', 'SPY'], axis=1)
        ax = df_temp.plot()
        ax.set_ylabel('Normalized Price')
        ax.set_xlabel('Date')

    # Add code here to properly compute end value
    ev = sv * (1 +cr)

    return cr, adr, sddr, sr, ev

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
    syms=['GOOG','AAPL','GLD','XOM'], gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    def f(allocs):
        normed = prices /prices.ix[0]
        alloced = normed * allocs
        port_val = alloced.sum(axis=1)
        daily_returns = port_val.copy()
        daily_returns[1:] = (port_val[1:] / port_val[:-1].values) -1
        daily_returns = daily_returns[1:]
        cr = (port_val[-1]/port_val[0])-1
        adr = daily_returns.mean()
        sddr = daily_returns.std()
        sr = np.sqrt(252) * adr /sddr
        return 1/sr

	
    # find the allocations for the optimal portfolio
    # note that the values here ARE NOT meant to be correct for a test case
	
    Xguess = np.ones(len(syms))/len(syms)
    optimized_result = spo.minimize(f,Xguess, method='SLSQP', \
                                    constraints=({'type': 'eq', 'fun': lambda inputs: 1 - np.sum(inputs)}), \
                                    bounds = [(0,1)] * len(syms)	
	)
    #
    allocs = optimized_result.x

    # Get daily portfolio value
    normed = prices /prices.ix[0]
    alloced = normed * allocs
    pos_vals = alloced * 1
    port_val = pos_vals.sum(axis=1)

    daily_returns = port_val.copy()
    daily_returns[1:] = (port_val[1:] / port_val[:-1].values) -1
    daily_returns = daily_returns[1:]

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cr = (port_val[-1]/port_val[0])-1
    adr = daily_returns.mean()
    sddr = daily_returns.std()
    sr = np.sqrt(252) * (adr -  0) /sddr
	
	
    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        df_temp = pd.concat([port_val/port_val.ix[0], prices_SPY/prices_SPY.ix[0]], keys=['Portfolio', 'SPY'], axis=1)
        ax = df_temp.plot()
        ax.set_ylabel('Normalized Price')
        ax.set_xlabel('Date')

    return allocs, cr, adr, sddr, sr

def ab_risk_ratio(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
    sym=['SPY'], \
    gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(sym, dates)  # automatically adds SPY
    prices = prices_all[sym]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value
    normed = prices /prices.ix[0]
    port_val = normed.sum(axis=1)

    daily_returns = prices_all.copy()
    daily_returns[1:] = (daily_returns[1:] / daily_returns[:-1].values) -1
    daily_returns = daily_returns[1:]
    beta,alpha = np.polyfit(daily_returns['SPY'],daily_returns[sym],1)
    corr = daily_returns.corr(method='pearson')
    if gen_plot:
      daily_returns.plot(kind='scatter', x='SPY', y=sym[0])
      plt.plot(daily_returns['SPY'], beta * daily_returns['SPY'] + alpha, '-', color='r')
      plt.show()
	
    return beta,alpha,corr
def test_code():
    # This code WILL NOT be tested by the auto grader
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!
    start_date = dt.datetime(2009,1,1)
    end_date = dt.datetime(2010,1,1)
    symbols = ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocations = [0.2, 0.3, 0.4, 0.1]
    start_val = 1000000  
    risk_free_rate = 0.0
    sample_freq = 252

    # Assess the portfolio
    cr, adr, sddr, sr, ev = assess_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        allocs = allocations,\
        sv = start_val, \
        gen_plot = False)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr

if __name__ == "__main__":
    test_code()
