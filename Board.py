# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re
import Marble as M


class Board():
    def __init__(self):
        """
        TODO
        """
        self.dimension = 9
        self.nb_white = self.nb_black = 14

        # We assume the standard initial configuration commonly used
        # So its hard-coded
        self.board = [[2, 2, 2, 2, 2, 0, 0, 0, 0],
                      [2, 2, 2, 2, 2, 2, 0, 0, 0],
                      [1, 1, 2, 2, 2, 1, 1, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 0, 1, 1, 3, 3, 3, 1, 1],
                      [0, 0, 0, 3, 3, 3, 3, 3, 3],
                      [0, 0, 0, 0, 3, 3, 3, 3, 3]]

    def __str__(self):
        """
        Display the current board's state
        Paremeters: None
        Returns: None
        """
        # 0: f = forbidden spot
        # 1: e = empty spot
        # 2: w = white marble
        # 3: b = black marble
        num_char = {"0": "f", "1": "e", "2": "w", "3": "b"}
        current_board = "  0 1 2 3 4 5 6 7 8    |         BOARD\n"
        mid_point = math.floor(self.dimension / 2)

        extra_space = 4 # For visibiliy purposes
        j, k = 1, mid_point
        for i in range(self.dimension):
            str_row = list(str(e) if e != 0 else " " for e in self.board[i])
            current_board += f"{i} " + " ".join(str_row) + extra_space * " " + "|   "
            if i < mid_point:
                current_board += k * " " + " ".join(str_row) + "\n"
                k -= 1
            elif i > mid_point:
                current_board += j * " " + " ".join(str_row).lstrip() + "\n"
                j += 1
            else:
                current_board += " ".join(str_row) + "\n"

        return current_board

    def count_marble(self):
        """
        TODO
        """
        gen_board = [item for sub_list in self.board for item in sub_list]

    def ask_move(self, marble_type):
        """ Ask the player his current move
        Parameters:
            None
        Return:
            type tuple of int (player's move)
        """
        while True:
            expr = r'^[0-9]{2}$'
            move = input('Pick a location on the board (08): ')
            if re.match(expr, move) is None:  # check if the move is correct
                print('Invalid move!')
                continue

            row, col = move
            current_move = self.board[int(row)][int(col)]
            # check if the player can play here
            if current_move == 0 or current_move == 1 or current_move != marble_type:
                print("current move=", current_move, sep="")
                print("You cannot play here!")
                continue

            orientation = input("Pick an orientation (N, S, E, W): ")
            if orientation.upper() not in ["N", "S", "E", "W"]: # check if the orientation is correct
                print("Invalid orientation!")
                continue

            print(row, col, orientation)

    def move_marble(self):
        """
        TODO
        """


if __name__ == "__main__":
    B = Board()
    print(B)
    # B.ask_move("a")
