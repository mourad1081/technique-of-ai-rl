import json
import operator
import random
import time

import numpy
from math import exp


class Agent:

    def __init__(self, ai, environment, nb_episodes, epsilon=-1, tau=-1, gamma=0.9):
        """
        Creates an agent in an environment.
        :param {str} ai: AI of the agent. Possible values: random|e-greedy|softmax
        :param {Labyrinth.Labyrinth} environment:
        :param {int} nb_episodes: Number of episodes for the training
        :param {float} epsilon: if selected ai is ε-greedy, represents the exploration rate (must be in range [0, 1])
        :param {float} tau: if selected ai is softmax, represents the temperature ([0, oo[)
        :param {float} gamma: Discount factor, must be in range [0, 1]
        """
        if ai == 'e-greedy' and epsilon == -1:
            raise ValueError("ε must be >= 0 if selected ai is ε-greedy !")
        if ai == 'softmax' and tau == -1:
            raise ValueError("τ must be >= 0 if selected ai is softmax !")

        self.ai = ai
        self.discount_rate = gamma
        self.tau = tau
        self.epsilon = epsilon
        self.nb_episodes = nb_episodes
        self.environment = environment

        self.policies = {
            'random':   self.pick_random_action,
            'e-greedy': self.e_greedy,
            'softmax':  self.softmax
        }

        self.observers = []
        self.current_location = (0, 0)
        self.current_episode = 1
        self.possible_actions = self.environment.get_possible_actions(*self.current_location)

        self.Q = \
            [
                [
                    {a: 0 for a in self.environment.get_possible_actions(i, j)}
                    for j in range(len(self.environment.adjacency_matrix[i]))
                ]
                for i in range(len(self.environment.adjacency_matrix))
            ]

        self.total_reward = 0.0
        self.total_reward_average = []
        self.total_selected_actions = {a: 0 for a in self.environment.actions}
        self.action_taken = None
        self.stop_learning = False
        self.stop = False

    def learn(self):
        learning_rates = numpy.linspace(1.0, 0.01, num=self.nb_episodes)
        epsilon_rates = numpy.linspace(self.epsilon, 0.001, num=self.nb_episodes)
        t = 1
        while t < self.nb_episodes and not self.stop:
            self.current_episode = t
            self.current_location = (0, 0)
            self.possible_actions = self.environment.get_possible_actions(*self.current_location)
            self.total_reward = 0.0
            self.total_reward_average = []
            self.epsilon = epsilon_rates[t]
            while not self.environment.is_out(*self.current_location) and not self.stop:
                action = self.policies[self.ai]()
                reward = self.environment.get_reward(self.current_location, action)
                # update our location and possible actions
                self.action_taken = action
                self.update_state(action, reward, t, learning_rates[t])
                self.total_selected_actions[action] += 1
                if self.environment.adjacency_matrix[self.current_location[0]][self.current_location[1]] == 0:
                    raise ValueError("je suis dans un endroit interdit !!!")
                time.sleep(0.1)
            t += 1

        self.export_q_values()

    def play(self):
        if not self.stop_learning:
            self.learn()
        else:
            self.optimal_play()

    def optimal_play(self):
        while not self.stop:
            self.current_location = (0, 0)
            self.possible_actions = self.environment.get_possible_actions(*self.current_location)
            self.total_reward = 0.0
            while not self.environment.is_out(*self.current_location) and not self.stop:
                self.action_taken = self.best_action()
                self.notify_observers()
                self.current_location = self.environment.get_location(*self.current_location, self.action_taken)
                self.possible_actions = self.environment.get_possible_actions(*self.current_location)
                if self.environment.adjacency_matrix[self.current_location[0]][self.current_location[1]] == 0:
                    raise ValueError("je suis dans un endroit interdit !!!")
                time.sleep(0.1)

    def export_q_values(self):
        with open('data.json', 'w') as outfile:
            json.dump(self.Q, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    def pick_random_action(self):
        random_action = random.choice(self.possible_actions)
        return random_action

    def best_action(self):
        (i, j) = self.current_location
        print("current location", self.current_location)
        print("possible actions", self.possible_actions)
        print("Q", self.Q[i][j])
        print("wtf ? ", [(k, v) for (k, v) in self.Q[i][j].items() if k in self.possible_actions])
        best_action = max([(k, v) for (k, v) in self.Q[i][j].items() if k in self.possible_actions], key=operator.itemgetter(1))[0]
        return best_action

    def e_greedy(self):
        return self.pick_random_action() if random.random() <= self.epsilon else self.best_action()

    def softmax(self):
        boltzmann_distribution = self.get_boltzmann_distribution(exponent_function=self.Q)
        action = self.generate_random(distribution=boltzmann_distribution)
        return action

    def Q(self, action):
        (i, j) = self.current_location
        return numpy.mean(self.Q[i][j][action]) if len(self.Q[i][j][action]) > 0 else 0.0

    def update_state(self, action, reward, current_episode, learning_rate):
        """

        :param {string} action:
        :param {float} reward:
        :param {int} current_episode:
        :return:
        """
        self.total_reward += reward
        (i, j) = self.current_location

        (new_i, new_j) = self.environment.get_location(i, j, action)
        next_possible_actions = self.environment.get_possible_actions(new_i, new_j)
        q_max = max([(k, v) for (k, v) in self.Q[new_i][new_j].items() if k in next_possible_actions], key=operator.itemgetter(1))[1]

        self.Q[i][j][action] += learning_rate * (reward + (self.discount_rate * q_max) - self.Q[i][j][action])

        self.notify_observers()

        self.current_location = (new_i, new_j)
        self.possible_actions = self.environment.get_possible_actions(*self.current_location)

        # self.total_reward_average.append(self.total_reward / (current_episode + 1))

    def get_boltzmann_distribution(self, exponent_function):
        distribution = []
        for a in self.possible_actions:
            denominator = 0.0
            for b in self.possible_actions:
                denominator += exp(exponent_function(b) / self.tau)
            distribution.append(exp(exponent_function(a) / self.tau) / denominator)
        return distribution

    def get_stats(self):
        return range(self.nb_episodes), self.total_reward_average, self.total_selected_actions

    def generate_random(self, distribution):
        return numpy.random.choice(self.possible_actions, p=distribution)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self):
        for o in self.observers:
            o.update_observation()
