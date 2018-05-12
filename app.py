import tkinter as tk

from Agent import Agent
from Labyrinth import Labyrinth
from LabyrinthGUI import LabyrinthGUI


if __name__ == '__main__':
    # We start by drawing the labyrinth
    map_labyrinth = [
        [1, 1, 2, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 2, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
        [1, 0, 1, 1, 0, 1, 1, 2, 1, 2, 0, 1, 2],
        [1, 0, 1, 1, 0, 1, 1, 2, 1, 2, 0, 1, 2],
        [1, 0, 1, 1, 0, 1, 1, 2, 1, 2, 0, 1, 2],
        [1, 0, 1, 1, 0, 1, 1, 2, 1, 2, 0, 1, 2],
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, -1],
    ]
    # then we define some hyper parameters
    nb_episodes = 99999
    environment = Labyrinth(map_labyrinth)
    policy = "softmax"  # e-greedy | random | softmax
    agent = Agent(policy, environment, nb_episodes, exploration_rate=0.7, temperature=50, discount_rate=0.95)

    # instantiate a window
    root = tk.Tk()
    root.resizable(0, 0)
    gui = LabyrinthGUI(root, environment, agent)
    # Let's go !
    root.mainloop()
