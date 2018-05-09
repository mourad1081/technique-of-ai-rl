import tkinter as tk

from Agent import Agent
from Labyrinth import Labyrinth
from LabyrinthGUI import LabyrinthGUI

map_labyrinth = [
    [1, 1, 2, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 2, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [1, 0, 1, 1, 0, 1, 1, 2, 1, 2, 0, 1, 2],
    [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 2],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 2, 1, 1],
    [1, 0, 2, 1, 0, 1, 1, 0, 2, 1, 2, 1, 1],
    [1, 0, 2, 1, 0, 1, 1, 0, 1, 1, 2, 1, 1],
    [1, 0, 2, 1, 0, 1, 1, 0, 1, 1, 2, 1, 1],
    [1, 0, 1, 1, 0, 1, 1, 2, 1, 1, 0, 1, 1],
    [1, 0, 2, 1, 0, 1, 1, 0, 1, 1, 0, 1, -1],
]


nb_episodes = 99999
nb_actions = 4
environment = Labyrinth(map_labyrinth)
agent = Agent("e-greedy", environment, nb_episodes, epsilon=0.2, gamma=0.95)

root = tk.Tk()
gui = LabyrinthGUI(root, environment, agent)
root.mainloop()
