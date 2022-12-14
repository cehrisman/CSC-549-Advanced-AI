import numpy as np
import random
import math
import copy


class SarsaLambdaFA:
    def __init__(self, fa, num_actions=None, alpha=0.01, gamma=1.0, lamb=0.9):
        self.gamma = gamma
        self.lamb = lamb
        self.alpha = alpha
        self.num_actions = num_actions
        self.fourier_basis = []

        for i in range(0, self.num_actions):
            self.fourier_basis.append(copy.deepcopy(fa))

        self.w = np.zeros([self.fourier_basis[0].coeff.shape[0], num_actions])
        self.z = np.zeros(self.w.shape)

        self.w[0, :] = 0.0

    def action(self, state):
        """
                Agent.action determines what action to take based on state

                :param state:
                :return action
        """
        best = -math.inf
        best_action = 0

        for a in range(0, self.num_actions):
            q = self.Q(state, a)
            if q > best:
                best = q
                best_action = a

        return best_action

    def Q(self, state, action):
        return np.dot(self.w[:, action], self.fourier_basis[action].get_features(state))

    def update(self, state, action, reward, next_state, done, next_action=None):
        """
            Agent.update updates the Q table based on the SARSA algorithm. It also updates the trace table

            :param next_action:
            :param done:
            :param next_state:
            :param state:
            :param action:
            :param reward
            :return None
        """

        delta = reward - self.Q(state, action)

        delta += self.gamma * self.Q(next_state, next_action)

        phi = self.fourier_basis[action].get_features(state)

        for a in range(0, self.num_actions):
            self.z[:, a] *= self.gamma * self.lamb
            if a == action:
                self.z[:, a] += phi
            self.w[:, a] += self.alpha * delta * np.multiply(self.fourier_basis[a].get_grad(), self.z[:,a])


        return delta
