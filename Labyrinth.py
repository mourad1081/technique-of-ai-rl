class Labyrinth:
    def __init__(self, adjacency_matrix):
        self.adjacency_matrix = adjacency_matrix
        self.actions = {"up", "down", "left", "right"}

    def get_possible_actions(self, i, j):
        """
        Returns the possible directions one can take given a (i,j) position in
        the labyrinth
        :param i: the y coordinate
        :param j: the x coordinate
        :return: array of possible actions
        """
        assert 0 <= i < len(self.adjacency_matrix)
        assert 0 <= j < len(self.adjacency_matrix[i])

        if self.adjacency_matrix[i][j] == 0:
            return []

        height = len(self.adjacency_matrix)
        width = len(self.adjacency_matrix[i])
        possible_actions = []

        # up - down
        if i - 1 >= 0 and self.adjacency_matrix[i - 1][j] != 0:
            possible_actions.append("up")
        if i + 1 < height and self.adjacency_matrix[i + 1][j] != 0:
            possible_actions.append("down")

        # left - right
        if j - 1 >= 0 and self.adjacency_matrix[i][j - 1] != 0:
            possible_actions.append("left")
        if j + 1 < width and self.adjacency_matrix[i][j + 1] != 0:
            possible_actions.append("right")

        return possible_actions

    def get_reward(self, state, action):
        """
        Get the reward for going to a location
        :param state: the current location
        :param action: where we want to go
        :return: a reward according to the new location
        """
        (i, j) = self.get_location(*state, action)
        if self.adjacency_matrix[i][j] == 1:
            return -1
        elif self.adjacency_matrix[i][j] == 2:
            return -10
        elif self.adjacency_matrix[i][j] == -1:
            return 10
        else:
            raise ValueError("location undefined")

    def is_out(self, i, j):
        return self.adjacency_matrix[i][j] == -1  # states for which an episode ends

    @staticmethod
    def get_location(i, j, direction):
        if direction == "up":
            return i - 1, j
        elif direction == "down":
            return i + 1, j
        elif direction == "left":
            return i, j - 1
        elif direction == "right":
            return i, j + 1
        else:
            error = "get_location::not a valid action. i=" + str(i) + ", j=" + str(j) + ", d=" + str(direction)
            raise ValueError(error)
