
# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re

from more_itertools import sliced
from termcolor import colored
from UserMessages import user_messages


class Board():

    r = "red"
    g = "green"
    c = "cyan"
    y = "yellow"

    # could also use ord(), but worse readibilty
    char_2_num = {
        "A": 0, "B": 1,"C": 2,"D": 3,"E": 4,
        "F": 5, "G": 6, "H": 7, "I": 8
    }

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
                      [1, 1, 2, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 2, 1, 1, 1, 1, 1],
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
            # type of movement (lateral or pushing)
            move_type = input(
                "Do you want to push marbles or perform a lateral move?\n"
                + "P: push, L: lateral: ").upper()

            # correct_push = (
            #     move_type.upper() in "LP" and
            #     len(set(x for x in move_type if x.isdigit())) == 1
            # )
            if move_type.upper() not in "LP":
                user_messages("ERR_MOVEMENT")
                continue

            if move_type == "P":
                expr = r"^([A-Z]\s?[1-9]\s?){2}$" 
                msg = "Select the first marble and its next position: "
            else:
                expr = r"^([A-Z][1-9]\s?){1,3}([A-Z][1-9]){1}"
                msg = "TODO"

            positions = input(msg)
            # check if the selection is correct
            if re.match(expr, positions, re.IGNORECASE) is None:  
                user_messages("ERR_INPUTS")
                continue

            # pairs value construction
            couples_hexa = tuple(sliced(positions, 2))

            # check if the selection of multiple marbles is correct
            # multiple marbles must be aligned along a common axis
            if move_type == "L":
                if (
                    not self.is_diagonal(couples_hexa)
                    and not self.is_horizontal(couples_hexa)
                ):
                    user_messages("ERR_MULTIPLE_MARBLES")
                    continue
            
                # pairs construction in the 2d list frame
                couples_square = (self.hexa_to_square(c) for c in couples_hexa)
                couples_square = tuple(couples_square)

                # check if all the selected marbles have the same color
                values = tuple(self.board[r][c] for r, c in couples_square)
                if not all(e == color for e in values):
                    user_messages("ERR_WRONG_MARBLES")
                    continue
            break
            
        return couples_hexa, move_type


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
                self.char_2_num[x], 
                int(y)
            )
        else:
            return (
                self.char_2_num[x], 
                int(y) + (ord(x) - ord("A")) - (self.middle + 1)
            )


    def update_board(self, couples, move_type, color):
        """
        TODO
        """
        enemy = color - 1 if color == 3 else color + 1
        sequence = dict()

        if move_type == "P":
            self.push_marbles(couples, color, sequence)
        else:
            self.move_marbles(couples, move_type)


        # Updating board
        for key, value in sequence.items():
            row, col = key
            self.board[row][col] = value


    def push_marbles(self, couples, color, sequence):
        """
        TODO
        """

        free = 1
        enemy = color - 1 if color == 3 else color + 1 # current enemy
        first, next = couples # the first marble and its next spot

        j = 1 if ord(first[0]) < ord(next[0]) else -1 # direction (up: 1, down: -1)
        k = 0 if first[1] == next[1] else -j # changing indexes (or not)
        r, c = self.hexa_to_square(first) # coordinates in the square frame

        sequence[(r, c)] = 1 # the first marble becomes an empty spot
        colors = [color] # storing the colors we meet

        # we first check that the selected marble is correct 
        # it cannot be an enemy or an empty spot
        if self.board[r][c] != color:
            user_messages("ERR_WRONG_MARBLES")
            self.ask_move(color)
            return
    
        while True:
            sumito = enemy in colors
            r, c = self.hexa_to_square(next)
            current_spot = self.board[r][c]
            if current_spot in (color, enemy): 
                colors.append(self.board[r][c])
            print(colors)

            # check if more than 3 marbles are being moved (forbidden)
            # or if a forbidden sumito is being performed (non-free spot after last enemy)
            too_much_marbles = colors.count(color) > 3
            wrong_sumito = colors.count(enemy) >= colors.count(color)

            if too_much_marbles or wrong_sumito:
                if too_much_marbles:
                    user_messages("ERR_TOO_MUCH")
                else:
                    user_messages("ERR_SUMITO")                     
                self.ask_move(color)
                return

            # if we keep finding our own marbles
            if current_spot == color and (r, c) not in sequence.keys():
                sequence[(r, c)] = color
            # we either find an enemy or an empty spot
            elif current_spot in (enemy, free):
                sequence[(r, c)] = enemy if sumito else color
                # if its an actual free spot, we break the while loop
                if current_spot == free:
                    break
            else:
                if colors[-1] == enemy:
                    user_messages("GG_KILLED_ENEMY")
                    self.marbles[enemy] -= 1
                else:
                    user_messages("WARN_SUICIDE")
                    self.marbles[color] -= 1
                break
            
            # getting the next spot
            next_row = f"{chr(ord(next[0]) + j)}"
            next_col = f"{int(next[1]) + int(k)}"
            next = f"{next_row + next_col}"


    def move_marbles(self, couples, orientation, color, sequence):
        """
        TODO        

        """
        enemy = color - 1 if color == 3 else color + 1

        for element in couples:
            r, c = element
            sequence[(r, c)] = 1 # all the initial spots become empty
            # to store the different colors (enemy or player's current color)

            n_r, n_c = self.get_next_spot(r, c, orientation)
            next_spot = self.board[n_r][n_c]
            if next_spot == color or next_spot == enemy:
                user_messages("ERR_MOVE_MULTIPLE")
                self.ask_move(color)
                return
            elif next_spot == 0:
                user_messages("WARN_SUICIDE")
                continue
            else:
                sequence[(n_r, n_c)] = color


    def is_diagonal(self, couples_hexa):
        """
        TODO
        """
        min_r = min(couples_hexa, key=lambda t: t[0])[0].upper()
        max_r = max(couples_hexa, key=lambda t: t[0])[0].upper()
        return (
            len(set(e[1] for e in couples_hexa)) == 1
            and ord(max_r) - ord(min_r) < len(couples_hexa)
        )


    def is_horizontal(self, couples_hexa):
        """
        TODO
        """
        # test along a horizontal line
        min_c = min(couples_hexa, key=lambda t: t[1])[1]
        max_c = max(couples_hexa, key=lambda t: t[1])[1]
        return (
            len(set(e[0] for e in couples_hexa)) == 1 
            and int(max_c) - int(min_c) < len(couples_hexa)
        )
                        

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
        r, g, c, y = self.r, self.g, self.c, self.y

        j = 1
        k = self.middle
        l = self.dimension
        sp = " " # space

        # 0: f = forbidden spot
        # 1: e = empty spot
        # 2: w = white marble
        # 3: b = black marble
        num_char = {
            "0": "f", 
            "1": "o",
            "2": colored("#", r, attrs=["bold"]), # ??
            "3": colored("x", g, attrs=["bold"])  # ??
        }

        current_board = f"{7 *sp}SQUARE {21* sp} HEXA\n" # first line
        current_board = colored(current_board, attrs=["bold"])
        for i in range(self.dimension):
            l_row = list(
                num_char[str(e)] if e != 0 else " " 
                for e in self.board[i]
            )
            current_board += f"{colored(i, c)} {sp.join(l_row)} {4 * sp}|   "
            letter = colored(str(chr(65 + i)), c) # chr(65) = "A"

            if i < self.middle:
                str_to_add = f"{k * sp}{letter} {sp.join(l_row).rstrip()}\n"
                current_board += str_to_add
                k -= 1
            elif i > self.middle:
                str_to_add = f"{j * sp}{letter} {sp.join(l_row).lstrip()}"
                current_board += f"{str_to_add} {colored(l, y)}\n"
                j += 1
                l -= 1
            else:
                current_board += f"{letter} {sp.join(l_row)}\n"
                
        # numbers bottom debug
        l_number = list(
            colored(str(e), y) 
            for e in range(0, 9)
        )
        # 13 to match the spaces
        r_numbers = " ".join(list(
            colored(str(e), y) for e in range(1, 6))
        )
        current_board += f"  {sp.join(l_number)} {13 * sp} {r_numbers}"

        return current_board

def main():
    B = Board()
    print(B)
    couples, orientation = B.ask_move(3)
    B.update_board(couples, orientation, 3)
    print(B)

    couples, orientation = B.ask_move(3)
    B.update_board(couples, orientation, 3)
    print(B)
    

    couples, orientation = B.ask_move(3)
    B.update_board(couples, orientation, 3)
    print(B)

if __name__ == "__main__": 
    main()
