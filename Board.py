# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re
import Marble as M
from rich.console import Console
from more_itertools import sliced


class Board():

    err_msg_style = "bold red"
    display_style = "bold blue"
    board_style = "bold green"

    def __init__(self):
        """
        TODO
        """
        self.dimension = 9
        self.middle = math.floor(self.dimension / 2)
        self.marbles = {2: 14, 3: 14}
        self.console = Console()

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
        Inputs:
            color
        Outputs:
            type tuple of int (player's move)
        """

        while True:
            expr = r"^([A-Z][1-9]\s?){1,3}$" 
            move = input("Pick your marble(s) (row-col: A-I, 0-8): ")
            # check if the move is correct
            if re.match(expr, move, re.IGNORECASE) is None:  
                self.console.print(
                    "Invalid selection!",
                     style=self.err_msg_style
                )
                continue

            # pair values construction
            couples_hexa = tuple(sliced(move, 2))
            couples_square = (self.hexa_to_square(c) for c in couples_hexa)
            couples_square = tuple(couples_square)

            # check if the selection of multiple marbles is correct
            # multiple marbles must be aligned along a common axis
            if len(couples_hexa) > 1:
                # test along a horizontal line
                min_c = min(couples_hexa, key=lambda t: t[1])[1]
                max_c = max(couples_hexa, key=lambda t: t[1])[1]
                horizontal = (
                    len(set(e[0] for e in couples_hexa)) == 1 
                    and int(max_c) - int(min_c) < len(couples_hexa)
                )

                # test along a diagonal
                min_r = min(couples_hexa, key=lambda t: t[0])[0].upper()
                max_r = max(couples_hexa, key=lambda t: t[0])[0].upper()
                diag_square = tuple()
                diagonal = (
                    len(set(e[1] for e in couples_square)) == 1
                    and ord(max_r) - ord(min_r) < len(couples_hexa)
                )

                if not diagonal and not horizontal:
                    self.console.print(
                        "You gotta select 3 linked marbles along a line!",
                        style=self.err_msg_style
                    )
                    continue

            # check if all the selected marbles have the same color
            values = tuple(self.board[r][c] for r, c in couples_square)
            if not all(e == color for e in values):
                self.console.print(
                    "You gotta chose your own marble!",
                    style=self.err_msg_style
                )
                continue
            break

        # if multiple marbles are moved w/o pushing
        # the orientations are restricted
        ori = ["W", "E", "NW", "SE"]
        if len(couples_hexa) == 1:
            ori.extend(["NE", "SW"]) # otherwise we consider all of them
            
        # check if the orientation is correct
        while True:
            sep = ", "
            orientation = input(f"Orientation ({sep.join(ori)})?: ").upper()
            if orientation.upper() not in ori: 
                self.console.print("Invalid orientation!", self.err_msg_style)
                continue
            
            return couples_square, orientation
            


    def hexa_to_square(self, coords_hexa):
        """
        Converts the BOARD coordinates (hexagonal) to DEBUG (square) coordinates
        Inputs:
            letter (string): first coordinate
            number (int): second coordinate
        Ouputs:
            x, y (tuple): DEBUG coordinates
        """
        x, y = coords_hexa.upper()
        if y in (self.middle, self.middle + 1):
            return (
                ord(x) - ord("A"), 
                int(y)
            )
        else:
            return (
                ord(x) - ord("A"), 
                int(y) + (ord(x) - ord("A")) - (self.middle + 1)
            )


    def move_marbles(self, couples, orientation, color):
        """
        TODO
        """
        enemy = color - 1 if color == 3 else color + 1
        multiple_marbles = len(couples) > 1

        for element in couples:
            r, c = element
            marbles_group = {(r, c): 1} # the first spot becomes empty
            colors = [] # to store the different colors (enemy or player's current color)

            # we first deal w/ multiple marbles withouh pushing
            # those marbles can only move to an empty spot
            if multiple_marbles:
                n_r, n_c = self.get_next_spot(r, c, orientation)
                next_spot = self.board[n_r][n_c]
                if next_spot == color or next_spot == enemy:
                    self.console.print(
                        "You cannot move your multiple marbles like this!",
                        style=self.err_msg_style
                    )
                    self.ask_move(color)
                    return
                elif next_spot == 0:
                    self.console.print(
                        "Suicide! GGs",
                        style=self.display_style
                    )
                    continue

            while True:
                sumito = enemy in colors
                
                # we keep finding our own marbles
                if self.board[r][c] == color and (r, c) not in marbles_group.keys():
                    marbles_group[(r, c)] = color
                # we either find an enemy or an empty spot
                elif self.board[r][c] == enemy or self.board[r][c] == 1:
                    marbles_group[(r, c)] = enemy if sumito else color
                    # if its an actual empty spot, we break the while loop
                    if self.board[r][c] == 1:
                        break

                colors.append(self.board[r][c])

                # check if more than 3 marbles are being moved (forbidden)
                # or if a forbidden sumito is being performed (non-free spot after last enemy)
                too_much_marbles = colors.count(color) > 3
                wrong_sumito = colors.count(enemy) >= colors.count(color)
                if too_much_marbles or wrong_sumito:
                    if too_much_marbles:
                        self.console.print(
                            "You cannot move more than 3 marbles!", 
                            style=self.err_msg_style
                        )
                    else:
                        self.console.print(
                            "You cannot perform a sumito like this!", 
                            style=self.err_msg_style
                        )                        
                    self.ask_move(color)
                    return

                r, c = self.get_next_spot(r, c, orientation) # next spot

        # updating board
        for key, value in marbles_group.items():
            row, col = key
            self.board[row][col] = value


    def get_next_spot(self, r, c, orientation):
        # displacements with black marbles as reference
        disp = {"E": lambda r, c: (r, c + 1),
                "W": lambda r, c: (r, c - 1), 
                "NE": lambda r, c: (r - 1, c),
                "NW": lambda r, c: (r - 1, c - 1),
                "SE": lambda r, c: (r + 1, c + 1),
                "SW": lambda r, c: (r + 1, c)
        }
        return disp[orientation](r, c)

            

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
        num_char = {"0": "f", "1": "o", "2": "#", "3": "x"}

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
    C.print(B, style=B.board_style)
    couples, orientation = B.ask_move(3)
    B.move_marbles(couples, orientation, 3)
    C.print(B, style=B.board_style)
    couples, orientation = B.ask_move(3)
    B.move_marbles(couples, orientation, 3)
    C.print(B, style=B.board_style)
        

if __name__ == "__main__": 
    main()
