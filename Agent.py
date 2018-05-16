import json
import operator
import random
import time

import numpy
from math import exp


class Agent:

    def __init__(self, policy, environment, nb_episodes, exploration_rate=-1,
                 temperature=-1, discount_rate=-1, learning_rate=0.9):
        """
        Creates an agent in an environment.
        :param {str} policy: AI of the agent. Possible values: random|e-greedy|softmax
        :param {Labyrinth.Labyrinth} environment:
        :param {int} nb_episodes: Number of episodes for the training
        :param {float} exploration_rate: if selected policy is ε-greedy,
                                         represents the exploration rate (must be in range [0, 1])
        :param {float} temperature: if selected ai is softmax,
                                    represents the temperature ([0, oo[)
        :param {float} discount_rate: Discount factor, must be in range [0, 1]
        """
        if policy == 'e-greedy' and (exploration_rate <= 0 or exploration_rate > 1):
            raise ValueError("Exploration rate must be in range [0, 1] if selected policy is ε-greedy !")
        if policy == 'softmax' and temperature <= 0:
            raise ValueError("Temperature must be in range [0, 1] if selected policy is softmax !")
        if discount_rate < 0 or discount_rate > 1:
            raise ValueError("Discount rate must be in range [0, 1] !")
        if learning_rate < 0 or learning_rate > 1:
            raise ValueError("Learning rate must be in range [0, 1] !")

        self.policy = policy
        self.temperature = temperature
        self.nb_episodes = nb_episodes
        self.environment = environment
        self.discount_rate = discount_rate
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate

        # Supported policies for this agent.
        self.policies = {
            # "name of the policy" : "reference to the function that handle that policy"
            'random': self.pick_random_action,
            'e-greedy': self.e_greedy,
            'softmax': self.softmax
        }

        # List of observer to update(GUI)
        self.observers = []
        self.current_episode = 1
        self.current_location = (0, 0)
        self.possible_actions = self.environment.get_possible_actions(*self.current_location)

        # Q values initialisation
        self.init_Q()

        self.total_reward = 0.0
        self.action_taken = None
        self.learning_done = False
        self.stop = False

    def init_Q(self):
        self.Q = []
        for i in range(len(self.environment.adjacency_matrix)):
            self.Q.append([])
            for j in range(len(self.environment.adjacency_matrix[i])):
                self.Q[i].append([])
                self.Q[i][j] = {action: 0 for action in self.environment.get_possible_actions(i, j)}

    def play(self):
        if self.learning_done:
            self.optimal_play()
        else:
            self.learn()

    def learn(self):
        """
        Starts the learning process of the agent.
        The agent learns with a Q-learning algorithm with a given policy.
        """
        t = 1
        while t < self.nb_episodes and not self.stop:
            self.current_episode = t
            self.current_location = (0, 0)
            self.possible_actions = self.environment.get_possible_actions(*self.current_location)
            self.total_reward = 0.0
            while not self.environment.is_out(*self.current_location) and not self.stop:
                action = self.policies[self.policy]()
                reward = self.environment.get_reward(self.current_location, action)
                # update our location and possible actions
                self.action_taken = action
                self.update_state(action, reward)
                if self.environment.adjacency_matrix[self.current_location[0]][self.current_location[1]] == 0:
                    raise ValueError("je suis dans un endroit interdit !!!")
                time.sleep(0.1)
            t += 1

    def optimal_play(self):
        """
        Plays in the environement by always taking the best action regarding the agent's Q values.
        The agent stops when the property self.stop is set to False.
        """
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
                    raise ValueError("Error: It seems that I am in a forbidden state.")
                time.sleep(0.1)

    def pick_random_action(self):
        """
        Takes a random action.
        :return: A random action
        """
        random_action = random.choice(self.possible_actions)
        return random_action

    def best_action(self):
        """
        Takes the best possible action for the current state.
        :return: The best action
        """
        (i, j) = self.current_location
        # The best action is the one that has the maximum Q value
        best_action = max(self.Q[i][j].items(), key=operator.itemgetter(1))[0]
        return best_action

    def e_greedy(self):
        """
        The e-greedy policy is defined as taking the best action
        with a probability 1-e and a random one with probability e.
        :return: The action that e-greedy has selected.
        """
        return self.pick_random_action() if random.random() <= self.exploration_rate else self.best_action()

    def softmax(self):
        boltzmann_distribution = self.get_boltzmann_distribution(exponent_function=self.Q)
        action = self.generate_random(distribution=boltzmann_distribution)
        return action

    def update_state(self, action, reward):
        """
        Updates the state of this agent.
        :param {string} action: The action the agent will take.
        :param {float} reward: The reward for taking that action.
        """
        self.total_reward += reward
        (i, j) = self.current_location
        # Get the reached state by taking this action
        (new_i, new_j) = self.environment.get_location(i, j, action)
        # We pick the best action of the next state regarding its Q value.
        q_max = max(self.Q[new_i][new_j].items(), key=operator.itemgetter(1))[1]
        # Update of the Q value function (A matrix is equivalent to a function in linear algebra).
        self.Q[i][j][action] += self.learning_rate * (reward + (self.discount_rate * q_max) - self.Q[i][j][action])
        # We first notify the observers that the agent's state has changed.
        self.notify_observers()
        # Then we update the next location and actions of the agent.
        self.current_location = (new_i, new_j)
        self.possible_actions = self.environment.get_possible_actions(*self.current_location)

    def get_boltzmann_distribution(self, exponent_function):
        """
        Generates a Boltzmann probability distribution with a custom exponent function.
        :param exponent_function: The exponent function.
        :return: A Boltzmann probability distribution.
        """
        assert self.temperature > 0, "Assertion error: tau must be grater than 0."

        distribution = []
        (i, j) = self.current_location
        for a in self.possible_actions:
            denominator = 0.0
            for b in self.possible_actions:
                denominator += exp(exponent_function[i][j][b] / self.temperature)
            distribution.append(exp(exponent_function[i][j][a] / self.temperature) / denominator)
        return distribution

    def generate_random(self, distribution):
        """
        Generates a random value from self.possible_actions following a probability distribution.
        :param distribution: A probability distribution (the sum of proba must be equals to 1)
        :return: A random value from self.possible_actions following a probability distribution
        """
        return numpy.random.choice(self.possible_actions, p=distribution)

    def add_observer(self, observer):
        """
        Adds an observers to this agent.
        :param observer: The observer
        """
        self.observers.append(observer)

    def notify_observers(self):
        """
        Notify the observers that the state of this agent has changed.
        """
        for o in self.observers:
            o.update_observation()
