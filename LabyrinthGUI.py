import random
import tkinter as tk
from tkinter.font import Font


class LabyrinthGUI(tk.Frame):
    def __init__(self, root, labyrinth, agent):
        tk.Frame.__init__(self, root)
        # Titre de la fenêtre
        self.root = root
        self.root.title("Labyrinthe magique")
        self.width = 1024
        self.height = 512
        self.square_width = 64
        self.square_height = 64

        self.root.config(width=self.width, height=self.height)
        # self.state('zoomed')
        # On créé la frame dans laquelle seront mis les boutons entre autre.
        # La belle couleur du fond est en hexa (trouvée sur internet) ici : https://flatuicolors.com/
        # On créé un canvas/zone de dessin (qui seront les plateaux) pour le joueur et l'ennemi
        self.labyrinth = labyrinth
        self.agent = agent
        self.agent.add_observer(self)
        self.position_agent_gui = None
        self.action_values = []

        # resources
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

        # widgets
        self.menu = tk.Frame(self.root, bg="#bdc3c7")
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.var = tk.BooleanVar()
        self.radio_learning_enabled = tk.Radiobutton(self.menu,  bg="#bdc3c7", variable=self.var, value=True, text="Apprentissage activé", command=self.enable_learning)
        self.radio_learning_disabled = tk.Radiobutton(self.menu, bg="#bdc3c7", variable=self.var, value=False, text="Apprentissage désactivé", command=self.disable_learning)

        self.customFont = Font(family='Helvetica', size=14, weight='bold')
        self.btn_start = tk.Button(self.menu, image=self.res["btn_start"], borderwidth=0, bg="#013243", command=self.start_learning)
        self.btn_stop = tk.Button(self.menu, image=self.res["btn_stop"], borderwidth=0, bg="#013243", command=self.stop_learning)
        # self.btn_export = tk.Button(self.menu, text='Export model', font=self.customFont, bg="#e67e22", fg="white", command=self.export)

        self.infos = tk.Label(self.menu, text="Etat AI", justify=tk.CENTER, fg='white', bg='#34495E')

        self.root.rowconfigure(0, weight=1)
        # self.root.columnconfigure(0, weight=1)

        self.menu.grid(row=0, column=0, sticky="nsew")
        self.canvas.grid(row=0, column=1, sticky="nsew")

        self.infos.grid(row=0, sticky="nsew", pady=5, padx=5)
        self.radio_learning_enabled.grid(row=1, pady=5, padx=5)
        self.radio_learning_disabled.grid(row=2, pady=5, padx=5)
        self.btn_start.grid(row=3, sticky="s", pady=5, padx=5)
        self.btn_stop.grid(row=4,  sticky="s",  pady=5, padx=5)

        self.menu.grid_rowconfigure(1, weight=1)
        self.menu.grid_rowconfigure(2, weight=1)
        self.menu.grid_rowconfigure(3, weight=20)
        self.menu.grid_rowconfigure(4, weight=2)
        # self.btn_export.pack(side=tk.BOTTOM, fill='x', expand=tk.YES, pady=5, padx=5)

        self.draw_grid()

    def draw_grid(self):
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
        pos = self.agent.current_location
        if self.position_agent_gui is not None:
            self.canvas.delete(self.position_agent_gui)

        self.position_agent_gui = self.canvas.create_image(pos[1] * self.square_width + 20,
                                                           pos[0] * self.square_height + 20,
                                                           image=self.res["pikachu"],
                                                           anchor='nw')

        value = "%.1f" % self.agent.Q[pos[0]][pos[1]][self.agent.action_taken]
        self.canvas.itemconfig(self.action_values[pos[0]][pos[1]][self.agent.action_taken], text=value)
        self.canvas.grid()
        self.canvas.update()

    def update_observation(self):
        self.infos['text'] = "Episode: " + str(self.agent.current_episode)
        self.update_position_agent()
