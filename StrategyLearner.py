import pandas as pd
import numpy as np
import datetime as dt
import util
import QLearner

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
        dyna = 10)


  def addEvidence(self,
        symbol = 'SPY',
        sd = dt.datetime(2008,1,1),
        ed = dt.datetime(2009,12,31),
        sv = 10000):
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
    cr_last = -1
    cr = 0
    while cr_last != cr:
      cr_last = cr
      self.holding = 0

      s = 0
      a = self.Q.querysetstate(0)
      actions = []
      if a == 0:
        self.holding = 1
        actions.append(100)
      else:
        self.holding = 0
        actions.append(0)
      r = 0
      s1 = (100 * self.holding) + df['qsma'].ix[1]
      for row in df.ix[1:].itertuples():
        a = self.Q.query(s1,r)
        if a == 0:
          if  self.holding == 1:
            actions.append(0)
            r = -50
          else:
            self.holding =1
            actions.append(100)
            r = 0
        elif a == 1:
          if self.holding == 0:
            actions.append(0)
            r = -50
          else:
            self.holding = 0
            actions.append(-100)
            r = row[5]
        elif a== 2:
          actions.append(0)
          if self.holding == 1:
            r = row[5]
          else:
            r = 0

        s1 = (100 * self.holding) + row[6]
        if self.verbose: print a,s1,r

      df = df.assign(actions=actions)
      ev = sv
      price = 0
      cr = 0
      for row in df.itertuples():
        if row[7] > 0:
          price = row[1]
        elif row[7] <0:
          cr = cr + (row[1] - price)*100
          price = 0
      print "CR: %f"%cr

  def testPolicy(self,
        symbol,
        sd, ed, sv):
    dates = pd.date_range(sd-dt.timedelta(100), ed)
    df = util.get_data([symbol],dates)[symbol]
    normalized = df/df.ix[0]
    sma = normalized.rolling(50).mean()
    df = pd.DataFrame(df).assign(normalized =normalized).assign(sma = sma).assign(psma = normalized / sma)[sd:]
    daily_returns = df[symbol].copy()
    daily_returns[1:] =  (df[symbol].ix[1:] / df[symbol].ix[:-1].values) -1
    daily_returns.ix[0] = 0
    df = df.assign(dr = daily_returns)
    df = df.assign(qsma = pd.qcut(df['sma'], 100, labels=False))
    s1=0
    self.holding = 0
    actions=[]
    for row in df.itertuples():
      a = self.Q.querysetstate(s1)

      if a == 0:
        if  self.holding == 1:
          actions.append(0)
        else:
          self.holding =1
          actions.append(100)
      elif a == 1:
        if self.holding == 0:
          actions.append(0)
        else:
          self.holding = 0
          actions.append(-100)
      elif a== 2:
        actions.append(0)
      s1 = (100 * self.holding) + row[6]
      if self.verbose: print a,s1,r

    df = df.assign(actions=actions)
    ev = sv
    price = 0
    cr = 0
    for row in df.itertuples():
      if row[7] > 0:
        price = row[1]
      elif row[7] <0:
        cr = cr + ((row[1] - price)*100)
        price = 0
    print "CR: %f"%cr
    print "Baseline: %f"%((df[symbol].ix[-1] - df[symbol].ix[0])*100)
