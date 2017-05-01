"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand

class QLearner(object):


    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.s = 0
        self.a = 0
        self.num_states = num_states
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna

        #initial setting of the Q table
        self.Q = np.random.uniform(low=-1.0, high=1.0, size=(num_states, num_actions))

        #initialize dyna per the lecture
        if self.dyna != 0:
            self.TCount = np.ndarray(shape=(num_states, num_actions, num_states))
            self.TCount.fill(0.00001)
            self.T = self.TCount / self.TCount.sum(axis=2, keepdims=True)
            self.R = np.ndarray(shape=(num_states, num_actions))
            self.R.fill(-1.0)

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        action = rand.randint(0, self.num_actions-1)
        if rand.random() > self.rar:
          action = np.argmax(self.Q[s_prime, ])
        if self.verbose: print "s =", s,"a =",action
        return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        #Update Q according to the formula from the lectures
        self.Q[self.s, self.a] = (1 - self.alpha) * self.Q[self.s, self.a] + self.alpha * (r + self.gamma * np.max(self.Q[s_prime, ]))

        #factor in the random action probability
        #if random, then we do a random action
        #if not random, we do the action that gives us the most reward
        if rand.random() <= self.rar:
            action = rand.randint(0, self.num_actions - 1)
        else:
            action = np.argmax(self.Q[s_prime, ])

        #factor in the discount rate
        self.rar = self.rar * self.radr

        #checks to see if we're doing dyna.
        if self.dyna != 0:
            #increment TCount according to the lectures
            self.TCount[self.s, self.a, s_prime] = self.TCount[self.s, self.a, s_prime] + 1
            #Update T using the formula in the lectures
            self.T = self.TCount / self.TCount.sum(axis=2, keepdims=True)

            #Update R according to the lecture formula
            self.R[self.s, self.a] = (1 - self.alpha) * self.R[self.s, self.a] + (self.alpha * r)

            #iterate through the number of acid trips
            for i in range(0, self.dyna):
                #select a random a and s
                aSimulated = np.random.randint(low=0, high=self.num_actions)
                sSimulated = np.random.randint(low=0, high=self.num_states)
                #infer s' from T
                s_primeSimulated = np.random.multinomial(1, self.T[sSimulated, aSimulated, ]).argmax()
                #compute R from s and a
                r = self.R[sSimulated, aSimulated]
                #update Q
                self.Q[sSimulated, aSimulated] = (1 - self.alpha) * self.Q[sSimulated, aSimulated] + self.alpha * (r + self.gamma * np.max(self.Q[s_primeSimulated,]))

        self.s = s_prime
        self.a = action
        if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        return action

if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
