import json
import random
import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font


class LabyrinthGUI(tk.Frame):
    """
    This class defines the main window look and feel.
    """

    def __init__(self, root, labyrinth, agent):
        """
        Creates a window that will show a visualisation of the agent exploring the labyrinth.
        :param root: a tkinter root window
        :param labyrinth: an instance of the labyrinth
        :param agent: an instance of the agent
        """
        tk.Frame.__init__(self, root)
        self.root = root
        # we define some parameters
        self.root.title("Labyrinthe magique")  # the title
        self.square_width = 64  # dimension of a tile
        self.square_height = 64  # dimension of a tile
        self.width = self.square_width * len(labyrinth.adjacency_matrix[0])  # the dimension
        self.height = self.square_height * len(labyrinth.adjacency_matrix)  # the dimension
        self.root.config(width=self.width, height=self.height)  # we set the dimension of the window

        # we store the instance of the labyrinth and the agent
        self.labyrinth = labyrinth
        self.agent = agent
        # we are an observer of the agent, we then add ourself to its list of observers
        self.agent.add_observer(self)
        # this tuple will contain the position of the agent
        self.position_agent_gui = None
        # this list will contain the numbers you visualise in red in the GUI
        self.action_values = []

        # image resources used in the GUI
        self.res = {
            "-1": tk.PhotoImage(file='img/-1.gif').zoom(2, 2),
            "-1b": tk.PhotoImage(file='img/-1.gif').zoom(2, 2),
            "0": tk.PhotoImage(file='img/0.gif').zoom(2, 2),
            "0b": tk.PhotoImage(file='img/0.gif').zoom(2, 2),
            "1": tk.PhotoImage(file='img/1.gif').zoom(2, 2),
            "1b": tk.PhotoImage(file='img/1b.gif').zoom(2, 2),
            "2": tk.PhotoImage(file='img/2.gif').zoom(2, 2),
            "2b": tk.PhotoImage(file='img/2b.gif').zoom(2, 2),
            "pikachu": tk.PhotoImage(file='img/pikachu.gif'),
            "btn_start": tk.PhotoImage(file="img/btn_start.ppm"),
            "btn_stop": tk.PhotoImage(file="img/btn_stop.ppm")
        }

        # here we define some widgets like a parent canvas, frame, some radio buttons, etc.
        self.menu = tk.Frame(self.root, bg="#2c3e50")
        self.canvas = tk.Canvas(self.root,
                                width=self.width,
                                height=self.height,
                                bg="#2c3e50")

        # Q learning parameter control
        self.slider_exp_rate = tk.Scale(self.menu, from_=0, to=1, bg="#2c3e50", fg="white",
                                        borderwidth="3",
                                        highlightthickness=0,
                                        orient=tk.HORIZONTAL,
                                        resolution=0.01,
                                        command=self.set_exp_rate)

        self.slider_exp_rate.set(0.1)

        self.slider_learning_rate = tk.Scale(self.menu, from_=0, to=1, bg="#2c3e50", fg="white",
                                             borderwidth="3",
                                             highlightthickness=0,
                                             orient=tk.HORIZONTAL,
                                             resolution=0.01,
                                             command=self.set_learning_rate)
        self.slider_learning_rate.set(0.95)

        self.slider_discount_rate = tk.Scale(self.menu, from_=0, to=1, bg="#2c3e50", fg="white",
                                             borderwidth="3",
                                             highlightthickness=0,
                                             orient=tk.HORIZONTAL,
                                             resolution=0.01,
                                             command=self.set_discount_rate)
        self.slider_discount_rate.set(0.8)

        self.slider_temperature = tk.Scale(self.menu, from_=0.01, to=20, bg="#2c3e50", fg="white",
                                           borderwidth="3",
                                           highlightthickness=0,
                                           orient=tk.HORIZONTAL,
                                           command=self.set_temperature,
                                           resolution=0.01)
        self.slider_temperature.set(0.01)

        self.label_learning = tk.Label(self.menu, text="Activate learning", fg='white', bg='#34495E')
        self.label_policy = tk.Label(self.menu, text="Learning policy", fg='white', bg='#34495E')

        self.label_exploration_rate = tk.Label(self.menu, text="Expl. rate", fg='white', bg='#34495E')
        self.label_temperature = tk.Label(self.menu, text="Temperature", fg='white', bg='#34495E')
        self.label_discount_rate = tk.Label(self.menu, text="Disc. rate", fg='white', bg='#34495E')
        self.label_learning_rate = tk.Label(self.menu, text="Learning rate", fg='white', bg='#34495E')

        self.var = tk.BooleanVar(value=True)
        # definition of the two radiobuttons
        self.radio_learning_enabled = tk.Radiobutton(self.menu,
                                                     bg="#2c3e50",
                                                     variable=self.var,
                                                     value=True,
                                                     text="Apprentissage activé",
                                                     fg="white",
                                                     selectcolor="black",
                                                     command=self.enable_learning)

        self.radio_learning_disabled = tk.Radiobutton(self.menu,
                                                      bg="#2c3e50",
                                                      variable=self.var,
                                                      value=False,
                                                      text="Apprentissage désactivé",
                                                      fg="white",
                                                      selectcolor="black",
                                                      command=self.disable_learning)

        self.type_policy = tk.StringVar(value="e-Greedy")
        self.radio_policy_egreedy = tk.Radiobutton(self.menu,
                                                   bg="#2c3e50",
                                                   variable=self.type_policy,
                                                   value="e-Greedy",
                                                   text="e-Greedy",
                                                   fg="white",
                                                   selectcolor="black",
                                                   command=self.set_egreedy_policy)

        self.radio_policy_softmax = tk.Radiobutton(self.menu,
                                                   bg="#2c3e50",
                                                   variable=self.type_policy,
                                                   value="softmax",
                                                   text="softmax",
                                                   fg="white",
                                                   selectcolor="black",
                                                   command=self.set_softmax_policy)

        self.radio_policy_random = tk.Radiobutton(self.menu,
                                                  bg="#2c3e50",
                                                  variable=self.type_policy,
                                                  value="random",
                                                  text="Aléatoire",
                                                  fg="white",
                                                  selectcolor="black",
                                                  command=self.set_random_policy)

        # here we define a custom font and the buttons we will put on the view
        self.customFont = Font(family='Helvetica', size=14, weight='bold')
        # the "command" parameter is a reference to the
        # function we call on the click event
        self.btn_start = tk.Button(self.menu,
                                   image=self.res["btn_start"],
                                   borderwidth=0,
                                   bg="#013243",
                                   command=self.start)

        self.btn_stop = tk.Button(self.menu,
                                  image=self.res["btn_stop"],
                                  borderwidth=0,
                                  bg="#013243",
                                  command=self.stop)

        self.btn_export = tk.Button(self.menu,
                                    text='Exporter modèle',
                                    font=self.customFont,
                                    bg="#e67e22",
                                    fg="white",
                                    command=self.export)

        self.btn_import = tk.Button(self.menu,
                                    text='Importer modèle',
                                    font=self.customFont,
                                    bg="#e67e22",
                                    fg="white",
                                    command=self.import_model)
        self.btn_import_map = tk.Button(self.menu,
                                        text='Importer labyrinthe',
                                        font=self.customFont,
                                        bg="#e67e22",
                                        fg="white",
                                        command=self.import_labyrinth)

        # this label will contain the number of the current episode.
        self.infos = tk.Label(self.menu,
                              text="Ètat AI",
                              justify=tk.CENTER,
                              fg='white',
                              bg='#34495E')

        # we use a gridpanel as layout, here i define the "weight" parameter as 1.
        # Doing so will make the widgets adaptate their dimension to the parent
        # layout even when we resize the window
        self.root.rowconfigure(0, weight=1)

        # here we tell that the menu frame will be placed in
        # the cell (0,0) and will be sticked to all sides even
        # on resize event
        self.menu.grid(row=0, column=0, sticky="nsew")

        # the labyrinth will be placed in the cell (0, 1)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        # the label will be placed on the cell (O, 0) of the menu (which has also a grid layout)
        self.infos.grid(row=0, columnspan=2, sticky="new", pady=5, padx=5)

        # the radio buttons will be placed on the cells (1, 0) and (2, 0)
        self.label_learning.grid(row=1, columnspan=2, pady=5, padx=5, sticky="ew")
        self.radio_learning_enabled.grid(row=2, columnspan=2, pady=5, padx=5, sticky="w")
        self.radio_learning_disabled.grid(row=3, columnspan=2, pady=5, padx=5, sticky="w")

        self.label_policy.grid(row=4, columnspan=2, pady=5, padx=5, sticky="ew")
        self.radio_policy_egreedy.grid(row=5, columnspan=2, pady=5, padx=5, sticky="w")
        self.radio_policy_softmax.grid(row=6, columnspan=2, pady=5, padx=5, sticky="w")
        self.radio_policy_random.grid(row=7, columnspan=2, pady=5, padx=5, sticky="w")

        self.label_exploration_rate.grid(row=8, column=0, pady=5, padx=5, sticky="ew")
        self.label_temperature.grid(row=8, column=1, pady=5, padx=5, sticky="ew")
        self.slider_exp_rate.grid(row=9, column=0, pady=5, padx=5, sticky="ew")
        self.slider_temperature.grid(row=9, column=1, pady=5, padx=5, sticky="ew")

        self.label_learning_rate.grid(row=10, column=0, pady=5, padx=5, sticky="ew")
        self.label_discount_rate.grid(row=10, column=1, pady=5, padx=5, sticky="ew")
        self.slider_learning_rate.grid(row=11, column=0, pady=5, padx=5, sticky="ew")
        self.slider_discount_rate.grid(row=11, column=1, pady=5, padx=5, sticky="ew")

        # the buttons are sticked on the bottom (s for "south", "nsew" for "north, outh, ease, west", etc)
        self.btn_start.grid(row=12, columnspan=2, sticky="s", pady=5, padx=5)
        self.btn_stop.grid(row=13, columnspan=2, sticky="s", pady=5, padx=5)
        self.btn_export.grid(row=14, column=0, sticky="s", pady=5, padx=5)
        self.btn_import.grid(row=14, column=1, sticky="s", pady=5, padx=5)
        self.btn_import_map.grid(row=15, columnspan=2, sticky="s", pady=5, padx=5)

        # we configure some rows of the menu frame by setting
        # their weight; a bigger weight means that the widget
        # at that row will take more space in the layout. we
        # do so in order to push the buttons at the very bottom
        # of the menu frame.
        self.menu.grid_rowconfigure(1, weight=1)
        self.menu.grid_rowconfigure(2, weight=1)
        self.menu.grid_rowconfigure(3, weight=1)
        self.menu.grid_rowconfigure(4, weight=1)
        self.menu.grid_rowconfigure(5, weight=1)
        self.menu.grid_rowconfigure(6, weight=1)
        self.menu.grid_rowconfigure(7, weight=1)
        self.menu.grid_rowconfigure(8, weight=1)
        self.menu.grid_rowconfigure(9, weight=1)
        self.menu.grid_rowconfigure(10, weight=1)
        self.menu.grid_rowconfigure(11, weight=1)
        self.menu.grid_rowconfigure(12, weight=20)
        self.menu.grid_rowconfigure(13, weight=1)
        self.menu.grid_rowconfigure(14, weight=1)
        self.menu.grid_rowconfigure(15, weight=1)

        # after every widgets are placed on the view,
        # we draw the view of the labyrinth
        self.draw_grid()

    def set_learning_rate(self, value):
        self.agent.learning_rate = float(value)

    def set_discount_rate(self, value):
        self.agent.discount_rate = float(value)

    def set_temperature(self, value):
        self.agent.temperature = float(value)

    def set_softmax_policy(self):
        self.agent.policy = "softmax"

    def set_egreedy_policy(self):
        self.agent.policy = "e-greedy"

    def set_random_policy(self):
        self.agent.policy = "random"

    def set_exp_rate(self, value):
        self.agent.exploration_rate = float(value)

    def draw_grid(self):
        """
        Draw a view of the labyrinth
        """
        for i in range(len(self.labyrinth.adjacency_matrix)):
            self.action_values.append([])
            for j in range(len(self.labyrinth.adjacency_matrix[i])):
                self.action_values[i].append([])
                # drawing grid
                alternate = "b" if random.random() <= .5 else ""
                self.canvas.create_image(j * self.square_width,
                                         i * self.square_height,
                                         image=self.res["1" + alternate],
                                         anchor='nw')
                if self.labyrinth.adjacency_matrix[i][j] != 1:
                    self.canvas.create_image(j * self.square_width,
                                             i * self.square_height,
                                             image=self.res[str(self.labyrinth.adjacency_matrix[i][j]) + alternate],
                                             anchor='nw')
                self.canvas.grid()

                # drawing action values
                possible_actions = self.labyrinth.get_possible_actions(i, j)
                self.action_values[i][j] = {}
                if "up" in possible_actions:
                    self.action_values[i][j]["up"] = self.canvas.create_text(j * self.square_width + 30,
                                                                             i * self.square_height + 20,
                                                                             fill="red",
                                                                             text=str(
                                                                                 "%.1f" % self.agent.Q[i][j]["up"]))
                if "down" in possible_actions:
                    self.action_values[i][j]["down"] = self.canvas.create_text(j * self.square_width + 30,
                                                                               i * self.square_height + 40,
                                                                               fill="red",
                                                                               text=str(
                                                                                   "%.1f" % self.agent.Q[i][j]["down"]))
                if "left" in possible_actions:
                    self.action_values[i][j]["left"] = self.canvas.create_text(j * self.square_width + 10,
                                                                               i * self.square_height + 30,
                                                                               fill="red",
                                                                               text=str(
                                                                                   "%.1f" % self.agent.Q[i][j]["left"]))
                if "right" in possible_actions:
                    self.action_values[i][j]["right"] = self.canvas.create_text(j * self.square_width + 50,
                                                                                i * self.square_height + 30,
                                                                                fill="red",
                                                                                text=str("%.1f" % self.agent.Q[i][j][
                                                                                    "right"]))

    def enable_learning(self):
        self.agent.learning_done = False

    def disable_learning(self):
        self.agent.learning_done = True

    def start(self):
        self.agent.stop = False
        self.radio_learning_disabled["state"] = tk.DISABLED
        self.radio_learning_enabled["state"] = tk.DISABLED
        self.agent.play()

    def stop(self):
        self.radio_learning_disabled["state"] = tk.ACTIVE
        self.radio_learning_enabled["state"] = tk.ACTIVE
        self.agent.stop = True

    def update_position_agent(self):
        (i, j) = self.agent.current_location
        if self.position_agent_gui is not None:
            self.canvas.delete(self.position_agent_gui)

        self.position_agent_gui = self.canvas.create_image(j * self.square_width + 20,
                                                           i * self.square_height + 20,
                                                           image=self.res["pikachu"],
                                                           anchor='nw')

        value = "%.1f" % self.agent.Q[i][j][self.agent.action_taken]
        self.canvas.itemconfig(self.action_values[i][j][self.agent.action_taken], text=value)
        self.canvas.grid()
        self.canvas.update()

    def update_observation(self):
        self.infos['text'] = "Episode: " + str(self.agent.current_episode)
        self.update_position_agent()

    def export(self):
        """
        Exports the Q values in a file (JSON format).
        """
        filename = filedialog.asksaveasfilename(initialdir="/",
                                                title="Select file",
                                                filetypes=(("Fichier JSON", "*.json"), ("Tous les fichiers", "*.*")))

        with open(filename, 'w') as outfile:
            json.dump({
                "q_values": self.agent.Q,
                "labyrinth": self.labyrinth.adjacency_matrix
            },
                outfile,
                sort_keys=True,
                indent=4,
                ensure_ascii=False)

    def import_model(self):
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select file",
                                              filetypes=(("Fichier JSON", "*.json"), ("Tous les fichiers", "*.*")))
        with open(filename, 'r') as infile:
            x = json.load(infile)

            self.labyrinth.adjacency_matrix = x["labyrinth"]
            self.agent.Q = x["q_values"]

            self.square_width = 64  # dimension of a tile
            self.square_height = 64  # dimension of a tile
            self.width = self.square_width * len(self.labyrinth.adjacency_matrix[0])  # the dimension
            self.height = self.square_height * len(self.labyrinth.adjacency_matrix)  # the dimension
            self.root.config(width=self.width, height=self.height)  # we set the dimension of the window
            self.action_values = []
            self.canvas.delete("all")
            self.draw_grid()
            self.update_observation()

    def import_labyrinth(self):
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select file",
                                              filetypes=(("Labyrinth map", "*.map"), ("Tous les fichiers", "*.*")))
        with open(filename, 'r') as infile:
            self.labyrinth.adjacency_matrix = []
            for line in infile.readlines():
                self.labyrinth.adjacency_matrix.append([int(x) for x in line.split(",")])
        print(len(self.labyrinth.adjacency_matrix))
        self.action_values = []
        self.agent.reset_Q()
        self.canvas.delete("all")
        self.draw_grid()
        self.update_observation()
