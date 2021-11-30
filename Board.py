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
        self.console = Console()

        # We assume the standard initial configuration commonly used
        # So its hard-coded
        self.board = [[2, 2, 2, 2, 2, 0, 0, 0, 0],
                      [2, 2, 2, 2, 2, 2, 0, 0, 0],
                      [1, 1, 2, 2, 2, 1, 1, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1, 0],
                      [1, 1, 2, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 2, 3, 1, 1, 1, 1],
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
                self.console.print("Invalid selection!", style="bold red")
                continue

            # pair values construction
            couples = tuple(sliced(move, 2))

            # check if the selection of multiple marbles is correct
            # multiple marbles must be aligned along a common axis
            if len(couples) > 1:
                min_r = min(couples, key=lambda t: t[0])[0].upper()
                max_r = max(couples, key=lambda t: t[0])[0].upper()
                horizontal = (
                    len(set(e[0] for e in couples)) == 1
                    and ord(max_r) - ord(min_r) < len(couples)
                )

                min_c = min(couples, key=lambda t: t[1])[1]
                max_c = max(couples, key=lambda t: t[1])[1]
                diagonal = (
                    len(set(e[1] for e in couples)) == 1 
                    and int(max_c) - int(min_c) < len(couples)
                )

                if not diagonal and not horizontal:
                    self.console.print(
                        "You gotta select 3 linked marbles along a line!",
                        style="bold red"
                    )
                    continue

            # pair values construction
            couples = self.hexa_to_square(couples) 
            # check if all the selected marbles have the same color
            values = tuple(self.board[row][col] for row, col in couples)
            if not all(e == color for e in values):
                self.console.print(
                    "You gotta chose your own marble!",
                    style="bold red"
                )
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
            orientation = input(f"Orientation ({sep.join(ori)})?: ").upper()
            if orientation.upper() not in ori: 
                self.console.print("Invalid orientation!", style="bold red")
                continue
            
            return couples, orientation
            


    def hexa_to_square(self, couples_hexa):
        """
        Converts the BOARD coordinates (hexagonal) to DEBUG (square) coordinates
        Inputs:
            letter (string): first coordinate
            number (int): second coordinate
        Ouputs:
            x, y (tuple): DEBUG coordinates
        """
        char_2_num = {
            "A": 0, "B": 1, "C": 2, "D": 3, "E": 4,
            "F": 5, "G": 6, "H": 7, "I": 8
        }
        couples_square = []
        for element in couples_hexa:
            x, y = element.upper()
            if y in (self.middle, self.middle + 1):
                couples_square.append((char_2_num[x], int(y)))
            else:
                couples_square.append((char_2_num[x], 
                int(y) + char_2_num[x] - (self.middle + 1)))

        return couples_square


    def move_marbles(self, couples, orientation, color):
        """
        TODO
        """
        enemy = color - 1 if color == 3 else color + 1

        for element in couples:
            r, c = element
            sumito = False

            if len(couples) == 1: # pushing marbles
                marbles_group = {(r, c): 1}
                colors = [self.board[r][c]]
                while True:
                    n_r, n_c = self.get_next_spot(r, c, orientation) # next spot

                    # check if more than 3 marbles are being moved (forbidden)
                    # or if a forbidden sumito is being performed (non-free spot after last enemy)
                    if all(e == color for e in colors) and len(colors) > 3:
                        if sumito:
                            self.console.print(
                                "You cannot perform a sumito like this!", 
                                style="bold red"
                            )
                        else:
                            self.console.print(
                                "You cannot move more than 3 marbles!", 
                                style="bold red"
                            )
                        self.ask_move(color)
                        return

                    # if we keep finding the same color
                    # we add to the marble group and associate the next color
                    if self.board[n_r][n_c] == color:
                        colors.append(self.board[n_r][n_c])
                        marbles_group[(n_r, n_c)] = color
                    # a free spot has been found 
                    elif self.board[n_r][n_c] == 1:
                        # if we perform a sumito, the free spot becomes an enemy
                        if sumito: 
                            marbles_group[(n_r, n_c)] = enemy
                        # othewise the free spot becomes the current marble
                        else:
                            marbles_group[(n_r, n_c)] = color
                        break
                    # possible valid sumito
                    elif self.board[n_r][n_c] == enemy:
                        colors.append(self.board[n_r][n_c])
                        if sumito:
                        # the enemy becomes the current marble
                            marbles_group[(n_r, n_c)] = enemy
                        else:
                            marbles_group[(n_r, n_c)] = color
                        sumito = True

                    # a marble has been ejected
                    else:
                        if self.board[r][c] == color: # killing a own marble on purpose
                            pass
                        else: # killing an enemy
                            pass

                    r, c = n_r, n_c

            print(marbles_group)

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
    C.print(B, style="bold green")
    couples, orientation = B.ask_move(3)
    B.move_marbles(couples, orientation, 3)
    C.print(B, style="bold green")
        

if __name__ == "__main__": 
    main()
