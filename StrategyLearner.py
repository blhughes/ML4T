import pandas as pd
import numpy as np
import datetime as dt
import util
import QLearner


class TradingEnvironment(object):
    class Action:
        BUY = 0
        SELL = 1
        WAIT = 2

    def __init__(self, symbol = 'SPY',
        sd = dt.datetime(2008,1,1),
        ed = dt.datetime(2009,12,31),
        sv = 10000,
        verbose=False):

        self.verbose = verbose
        self.symbol = symbol
        self.cash = sv
        self.sv = sv
        self.shares = 0

        dates = pd.date_range(sd-dt.timedelta(100), ed)
        df = util.get_data([symbol],dates)[symbol]
        normalized = df/df.ix[0]
        sma = normalized.rolling(50).mean()
        df = pd.DataFrame(df).assign(normalized =normalized).assign(sma = sma).assign(psma = normalized / sma)[sd:]
        daily_returns = df[symbol].copy()
        daily_returns[1:] =  (df[symbol].ix[1:] / df[symbol].ix[:-1].values) -1
        daily_returns.ix[0] = 0
        df = df.assign(dr = daily_returns)
        df = df.assign(qsma = pd.qcut(df['psma'], 100, labels=False))

        self.df = df
        self.market = df.iterrows()
        self.current_stats = self.market.next()
        self.action = self.Action()

    def buy(self):
        if self.shares >= 200:
          return -10000 #Invalid purchase
        if self.verbose: print "Buy 100 @ %0.2f" %(self.current_stats[1][self.symbol])
        self.shares = self.shares + 100
        self.cash = self.cash - (100 * self.current_stats[1][self.symbol] ) # Closing price
        dr = 100 * self.current_stats[1]['dr']
        return dr #Reward

    def sell(self):
        if self.shares <= 0:
          return -10000 #Invalid sale
        if self.verbose: print "SELL 100 @ %0.2f" %(self.current_stats[1][self.symbol])
        self.shares = self.shares - 100
        self.cash = self.cash + (100 * self.current_stats[1][self.symbol]) # Closing price
        return (self.cash - self.sv) + (self.shares * self.current_stats[1][self.symbol]) #Reward

    def wait(self):
        if self.verbose: print "WAIT @ %0.2f" %(self.current_stats[1][self.symbol])
        dr = self.shares * self.current_stats[1]['dr']
        return dr

    def discritize_state(self):
        norm = pd.cut(self.df['normalized'], 10, labels=False)
        psma = pd.cut(self.df['psma'], 10, labels=False)
        date = self.current_stats[0]
        return (self.shares) + norm[date] * 10 + psma[date]

    def increment(self,action):
        # Calculate reward based on action
        r = {
          self.action.BUY:  self.buy,
          self.action.SELL: self.sell,
          self.action.WAIT: self.wait,
        }[action]()

        # Move foward one day and calculate new state
        try:
          self.current_stats = self.market.next()
          s = self.discritize_state()
        except StopIteration:
          return None,None
        return s,r #state, reward

    def state(self):
      cv = self.shares *self.current_stats[1][self.symbol] + self.cash
      return (cv,self.cash,self.shares,self.current_stats[1][self.symbol])

    def baseline(self):
      cr = self.sv + ((self.df[self.symbol].ix[-1] - self.df[self.symbol].ix[0]) * 100)
      return cr


class StrategyLearner(object):
  def __init__(self, verbose = False):
    self.verbose = verbose
    self.Q = QLearner.QLearner(
        num_states = 1000,
        num_actions = 3,
        alpha = 0.2,
        gamma = 0.9,
        rar = 0.5,
        radr = 0.99,
        dyna = 200)


  def addEvidence(self,
        symbol = 'SPY',
        sd = dt.datetime(2008,1,1),
        ed = dt.datetime(2009,12,31),
        sv = 10000):


      cr =0
      cr_last = -1
      while cr != cr_last:
        tenv = TradingEnvironment(symbol, sd, ed, sv, self.verbose)
        s = tenv.discritize_state()
        a = self.Q.querysetstate(s)
        while True:
          s1,r = tenv.increment(a)
          if s1 is None:
            break
          a = self.Q.query(s1,r)

        print tenv.state()
        cr_last = cr
        cr = tenv.state()[0]


  def testPolicy(self,
        symbol,
        sd, ed, sv, verbose=False):
    tenv = TradingEnvironment(symbol, sd, ed, sv, self.verbose)
    s = tenv.discritize_state()
    a = self.Q.querysetstate(s)
    while True:
      s1,r = tenv.increment(a)
      if s1 is None:
        break
      a = self.Q.querysetstate(s1)
      if verbose: print s1,r,a

    print "CR: %0.2f" %(tenv.state()[0] / sv) 
    print "Baseline: %0.2f" %(tenv.baseline() / sv)

