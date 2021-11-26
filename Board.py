# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re
import Marble as M
from rich.console import Console


class Board():
    def __init__(self):
        """
        TODO
        """
        self.dimension = 9
        self.middle = math.floor(self.dimension / 2)
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

    def count_marble(self):
        """
        TODO
        """
        gen_board = [item for sub_list in self.board for item in sub_list]

    def hexa_to_square(self, number, letter):
        """
        Converts the BOARD (hexagonal) to DEBUG (square) coordinates
        Parameters:
            letter (string): first coordinate
            number (int): second coordinate
        Returns:
            x, y (tuple): DEBUG coordinates
        """
        char_2_num = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4,
                    "F": 5, "G": 6, "H": 7, "I": 8
        }
        y = char_2_num[letter.upper()]
        if y in (self.middle, self.middle + 1):
            return y, number
        elif y > self.middle + 1:
            return y, number + 1
        else:
            return y, number - 2

    def ask_move(self, marble_type):
        """ Ask the player his current move
        Parameters:
            Noneg
        Return:
            type tuple of int (player's move)
        """

        while True:
            expr = r'^[A-I][0-8]$'
            move = input("""Pick a location on right the board
                         (row-col: A-I, 0-8): """)
            if re.match(expr, move.upper()) is None:  # check if the move is correct
                print('Invalid move!')
                continue

            y, x = move
            # conversion needed to match the actual board
            row, col = self.hexa_to_square(int(x), y)
            current_move = self.board[row][col]
            # check if the player can play here
            if current_move == 0 or current_move == 1 or current_move != marble_type:
                print(row, col, current_move)
                print("You cannot play here!")
                continue
            break

        # check if the orientation is correct
        while True:
            orientation = input("Pick an orientation (E, W, NE, NW, SE, SW): ")
            if orientation.upper() not in ["E", "W", "NE", "NW", "SE", "SW"]: 
                print("Invalid orientation!")
                continue
            break

        return (row, col), orientation


    def move_marble(self, move, orientation, marble_type):
        """
        TODO
        """
        row, col = move
        print(row, col)
        print(self.board[row][col])

        # displacements with black marbles as reference
        disp = {"E": (row, col + 1), 
                "W": (row, col - 1), 
                "NE": (row - 1, col),
                "NW": (row - 1, col - 1), 
                "SE": (row + 1, col + 1), 
                "SW": (row + 1, col)
        }
        print("move=", move)
        x, y = disp[orientation.upper()]
        print("x, y=", x, y)
        self.board[x][y] = marble_type
        self.board[row][col] = 1 # the spot becomes empty

    def __str__(self):
        """
        Display the current board's state
        Two boards are displayed:
        Debug that corresponds to the 2D-list w/ the associated indexes
        Board shows the actual play board 
        Paremeters: 
            None
        Returns: 
            None
        """
        # 0: f = forbidden spot
        # 1: e = empty spot
        # 2: w = white marble
        # 3: b = black marble
        num_char = {"0": "f", "1": "e", "2": "w", "3": "b"}

        j = 1
        k = self.middle
        l = self.dimension
        sp = " " # space

        current_board = f"{7 *sp} DEBUG {20 * sp} BOARD\n" # first line
        for i in range(self.dimension):
            l_row = list(num_char[str(e)] if e != 0 else " " for e in self.board[i])
            current_board += f"{i} {sp.join(l_row)} {4 * sp}|   "
            letter = str(chr(65 + i)) # chr(65) = "A"
            if i < self.middle:
                str_to_add = f"{k * sp}{letter} {sp.join(l_row).rstrip()}\n"
                current_board += str_to_add
                k -= 1
            elif i > self.middle:
                str_to_add = f"{j * sp}{letter} {sp.join(l_row).lstrip()} {l}\n"
                current_board += str_to_add
                j += 1
                l -= 1
            else:
                current_board += f"{letter} {sp.join(l_row)}\n"
                
        # numbers bottom debug
        l_number = list(str(e) for e in range(0, 9))
        # 13 to match the spaces
        current_board += f"  {sp.join(l_number)} {13 * sp} 1 2 3 4 5"
        return current_board

if __name__ == "__main__": 
    C = Console()
    B = Board()
    C.print(B, style="bold green")
    move, orientation = B.ask_move(3)
    B.move_marble(move, orientation, 3)
    C.print(B, style="bold green")
    
