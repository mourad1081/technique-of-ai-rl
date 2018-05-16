import tkinter as tk

from Agent import Agent
from Labyrinth import Labyrinth
from LabyrinthGUI import LabyrinthGUI


if __name__ == '__main__':
    # We start by drawing the labyrinth
    """
    0 : Closed path (rock)
    1 : Free path
    2 : Trap
    -1: Goal
    """
    map_labyrinth = [
        [1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1],
        [2, 0, 2, 1, -1]
    ]
    # then we define some hyper parameters
    nb_episodes = 50
    environment = Labyrinth(map_labyrinth)
    policy = "e-greedy"  # e-greedy | random | softmax
    agent = Agent(policy, environment, nb_episodes, exploration_rate=0.5, temperature=10, discount_rate=0.5, learning_rate=0.5)

    # instantiate a window
    root = tk.Tk()
    root.resizable(0, 0)
    gui = LabyrinthGUI(root, environment, agent)
    # Let's go !
    root.mainloop()
