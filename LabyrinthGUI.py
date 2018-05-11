import random
import tkinter as tk
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
        self.width = 1024  # the dimension
        self.height = 512  # the dimension
        self.square_width = 64  # dimension of a tile
        self.square_height = 64  # dimension of a tile
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
        self.menu = tk.Frame(self.root, bg="#bdc3c7")
        self.canvas = tk.Canvas(self.root,
                                width=self.width,
                                height=self.height,
                                bg="black")
        # definition of the two radiobuttons
        self.var = tk.BooleanVar()
        self.radio_learning_enabled = tk.Radiobutton(self.menu,
                                                     bg="#bdc3c7",
                                                     variable=self.var,
                                                     value=True,
                                                     text="Apprentissage activé",
                                                     command=self.enable_learning)

        self.radio_learning_disabled = tk.Radiobutton(self.menu,
                                                      bg="#bdc3c7",
                                                      variable=self.var,
                                                      value=False,
                                                      text="Apprentissage désactivé",
                                                      command=self.disable_learning)

        # here we define a custom font and the buttons we will put on the view
        self.customFont = Font(family='Helvetica', size=14, weight='bold')
        # the "command" parameter is a reference to the
        # function we call on the click event
        self.btn_start = tk.Button(self.menu,
                                   image=self.res["btn_start"],
                                   borderwidth=0,
                                   bg="#013243",
                                   command=self.start_learning)

        self.btn_stop = tk.Button(self.menu,
                                  image=self.res["btn_stop"],
                                  borderwidth=0,
                                  bg="#013243",
                                  command=self.stop_learning)

        self.btn_export = tk.Button(self.menu,
                                    text='Exporter Q values',
                                    font=self.customFont,
                                    bg="#e67e22",
                                    fg="white",
                                    command=self.export)

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
        self.infos.grid(row=0, sticky="nsew", pady=5, padx=5)

        # the radio buttons will be placed on the cells (1, 0) and (2, 0)
        self.radio_learning_enabled.grid(row=1, pady=5, padx=5)
        self.radio_learning_disabled.grid(row=2, pady=5, padx=5)

        # the buttons are sticked on the bottom (s for "south", "nsew" for "north, outh, ease, west", etc)
        self.btn_start.grid(row=3, sticky="s", pady=5, padx=5)
        self.btn_stop.grid(row=4, sticky="s", pady=5, padx=5)
        self.btn_export.grid(row=5, sticky="s", pady=5, padx=5)

        # we configure some rows of the menu frame by setting
        # their weight; a bigger weight means that the widget
        # at that row will take more space in the layout. we
        # do so in order to push the buttons at the very bottom
        # of the menu frame.
        self.menu.grid_rowconfigure(1, weight=1)
        self.menu.grid_rowconfigure(2, weight=1)
        self.menu.grid_rowconfigure(3, weight=20)
        self.menu.grid_rowconfigure(4, weight=1)
        self.menu.grid_rowconfigure(5, weight=1)

        # after every widgets are placed on the view, we draw the view of the labyrinth
        self.draw_grid()

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
                                                                                 self.labyrinth.get_reward((i, j),
                                                                                                           "up")))
                if "down" in possible_actions:
                    self.action_values[i][j]["down"] = self.canvas.create_text(j * self.square_width + 30,
                                                                               i * self.square_height + 40,
                                                                               fill="red",
                                                                               text=str(
                                                                                   self.labyrinth.get_reward((i, j),
                                                                                                             "down")))
                if "left" in possible_actions:
                    self.action_values[i][j]["left"] = self.canvas.create_text(j * self.square_width + 10,
                                                                               i * self.square_height + 30,
                                                                               fill="red",
                                                                               text=str(
                                                                                   self.labyrinth.get_reward((i, j),
                                                                                                             "left")))
                if "right" in possible_actions:
                    self.action_values[i][j]["right"] = self.canvas.create_text(j * self.square_width + 50,
                                                                                i * self.square_height + 30,
                                                                                fill="red",
                                                                                text=str(
                                                                                    self.labyrinth.get_reward((i, j),
                                                                                                              "right")))

    def enable_learning(self):
        self.agent.stop_learning = False

    def disable_learning(self):
        self.agent.stop_learning = True

    def start_learning(self):
        self.agent.stop = False
        self.agent.play()

    def stop_learning(self):
        self.agent.stop = True

    def export(self):
        self.agent.export_q_values()

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
