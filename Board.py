# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re
import Marble as M
from rich.console import Console
from more_itertools import sliced


class Board():
    def __init__(self):
        """
        TODO
        """
        self.dimension = 9
        self.middle = math.floor(self.dimension / 2)
        self.marbles = {2: 14, 3: 14}

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


    def ask_move(self, color):
        """ Ask the player his current move
        Parameters:
            color
        Return:
            type tuple of int (player's move)
        """

        while True:
            expr = r"^([A-Z][1-9]\s?){1,3}$" 
            move = input("Pick your marble(s) (row-col: A-I, 0-8): ")
            # check if the move is correct
            if re.match(expr, move, re.IGNORECASE) is None:  
                print('Invalid coordinates!')
                continue

            # extraction of marble couples
            couples = self.hexa_to_square(tuple(sliced(move, 2))) 
            values = tuple(self.board[row][col] for row, col in couples)
            if not all(e == color for e in values):
                print("You gotta chose your own marble!")
                continue
            break

        # if multiple marbles are moved w/o pushing
        # the orientations are restricted
        ori = ["W", "E", "NW", "SE"]
        if len(couples) == 1:
            ori.extend(["NE", "SW"]) # otherwise we consider all of them
            
        # check if the orientation is correct
        while True:
            sep = ", "
            orientation = input(f"Orientation ({sep.join(ori)})?: ")
            if orientation.upper() not in ori: 
                print("Invalid orientation!")
                continue
            
            return couples, orientation
            


    def hexa_to_square(self, couples_hexa):
        """
        Converts the BOARD coordinates (hexagonal) to DEBUG (square) coordinates
        Parameters:
            letter (string): first coordinate
            number (int): second coordinate
        Returns:
            x, y (tuple): DEBUG coordinates
        """
        char_2_num = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4,
                    "F": 5, "G": 6, "H": 7, "I": 8
        }
        couples_square = []
        for element in couples_hexa:
            x, y = element.upper()
            if y in (self.middle, self.middle + 1):
                couples_square.append((char_2_num[x], int(y)))
            else:
                couples_square.append((char_2_num[x], 
                int(y) + char_2_num[x] - (self.middle + 1))
                )

        return couples_square


    def move_marble(self, couples, orientation, color):
        """
        TODO
        """
        new_couples = []
        enemy = color - 1 if color == 3 else color + 1

        # displacements with black marbles as reference
        disp = {"E": lambda r, c: (r, c + 1),
                "W": lambda r, c: (r, c - 1), 
                "NE": lambda r, c: (r - 1, c),
                "NW": lambda r, c: (r - 1, c - 1),
                "SE": lambda r, c: (r + 1, c + 1),
                "SW": lambda r, c: (r + 1, c)
        }

        # not using list comprehension for better readibility
        for element in couples:
            r, c = element
            n_r, n_c = disp[orientation.upper()](r, c)
            
            if self.board[n_r][n_c] == color or self.board[n_r][n_c] == enemy:
                print("NO!")
                continue

            if self.board[n_r][n_c] == 0:
                self.marbles[color] -= 1
                print("Suicide! GGs")
                continue

            # updating board
            self.board[r][c] = 1
            self.board[n_r][n_c] = color
            

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
        num_char = {"0": "f", "1": "o", "2": "w", "3": "b"}

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

def main():
    C = Console()
    B = Board()
    C.print(B, style="bold green")
    couples, orientation = B.ask_move(3)
    B.move_marble(couples, orientation, 3)
    C.print(B, style="bold green")
        

if __name__ == "__main__": 
    main()
