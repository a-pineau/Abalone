
# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re

from more_itertools import sliced
from termcolor import colored
from UserMessages import err_messages, info_messages, ask_messages


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
                      [1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 0, 1, 1, 3, 3, 3, 1, 1],
                      [0, 0, 0, 3, 3, 3, 3, 3, 3],
                      [0, 0, 0, 0, 3, 3, 3, 3, 3]]

    def enemy(self, color):
        """
        TODO
        """
        return color + 1 if color == 2 else color - 1


    def ask_move(self, color):
        """ Ask the player his current move
        Inputs:
            color
        Outputs:
            type tuple of int (player's move)
        """
        enemy = self.enemy(color)
        valid_move = False
        while not valid_move:
            # type of movement (lateral or pushing)
            move_type = input(ask_messages("ASK_MVT")).upper()

            if move_type.upper() not in "PF":
                err_messages("ERR_MOVEMENT")
                continue

            if move_type == "P":
                expr = r"^([A-Z]\s?[1-9]\s?){2}$" 
                msg = ask_messages("ASK_P_MARBLES")
            else:
                expr = r"^([A-Z][1-9]\s?){1,3}\s?([A-Z][1-9]){1}"
                msg = ask_messages("ASK_F_MARBLES")
                       

            positions = input(colored(msg, attrs=["bold"]))
            positions = positions.replace(" ", "")
            # check if the selection is correct
            if re.match(expr, positions, re.IGNORECASE) is None:  
                err_messages("ERR_INPUTS")
                continue

            # pairs value construction
            couples_hexa = tuple(sliced(positions, 2))

            # pairs construction in the 2d list frame
            couples_square = (self.hexa_to_square(c) 
                              for c in couples_hexa)
            couples_square = tuple(couples_square)

            # check if all the selected marbles have the same color
            values = tuple(self.board[r][c] for r, c in couples_square)
            if enemy in values:
                err_messages("ERR_WRONG_MARBLES")
                continue

            valid_move = True
        
        # board update
        self.update_board(couples_hexa, move_type, color, enemy)


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


    def update_board(self, couples, move_type, color, enemy):
        """
        TODO
        """
        enemy = color - 1 if color == 3 else color + 1
        sequence = dict()

        if move_type == "P":
            self.push_marbles(couples, sequence, color, enemy)
        else:
            self.move_marbles(couples, sequence, color, enemy)

        for key, value in sequence.items():
            row, col = key
            self.board[row][col] = value


    def move_marbles(self, couples, sequence, color, enemy):
        """
        TODO        
        """
        friend = color 
        marbles_range, next = list(couples[:-1]), couples[-1] 
        first, last = marbles_range

        # lengths (rows, columns) of the range
        l_row = abs(ord(last[0]) - ord(first[0]))
        l_col = abs(int(last[1]) - int(first[1]))

        # the range cannot have more than 3 marbles
        if any(l > 2 for l in (l_row, l_col)):
            err_messages("ERR_RANGE")
            self.ask_move(color)
            return

        range_3_marbles = any(l == 2 for l in (l_row, l_col))

        # range of 3 marbles, we need to find the middle one
        # as the user provides w/ the first and the last marble
        if range_3_marbles:
            mid_marble = self.middle_marble(marbles_range, 
                                                    color)
            marbles_range.insert(1, mid_marble)

        # check if the range does not contain empty spots or enemies
        couples_square = (self.hexa_to_square(e) for e in marbles_range)
        if any(self.board[r][c] != friend for r, c in couples_square):
            err_messages("ERR_NONFRIENDLY_RANGE")
            self.ask_move(color)
            return

        j, k = self.predict_direction(marbles_range[0], 
                                      marbles_range[1])
        for couple in marbles_range:
            valid_neighborhood = self.valid_neighborhood(couple, 
                                                         color,
                                                         enemy)
            r, c = self.hexa_to_square(couple)
            n_r, n_c = self.hexa_to_square(next)
            if (n_r, n_c) not in valid_neighborhood:
                err_messages("ERR_MOVE_RANGE")
                self.ask_move(color)
                return
            sequence[(r, c)] = 1
            sequence[(n_r, n_c)] = color

            # getting the next spot
            next_row = chr(ord(next[0]) + j)
            next_col = int(next[1]) + int(k)
            next = f"{next_row}{next_col}"



    def push_marbles(self, couples, sequence, color, enemy):
        """
        TODO
        """

        free = 1
        friend = color
        enemy = friend - 1 if friend == 3 else friend + 1 # current enemy
        first, next = couples # the first marble and its next spot
        j, k = self.predict_direction(first, next)

        r, c = self.hexa_to_square(first) # coordinates in the square frame

        sequence[(r, c)] = 1 # the first marble becomes an empty spot
        colors = [friend] # storing the colors we meet

        # we first check that the selected marble is correct 
        # it cannot be an enemy or an empty spot
        if self.board[r][c] != friend:
            err_messages("ERR_WRONG_MARBLES")
            self.ask_move(friend)
            return
    
        end_move = False # better readibilty than a while True
        while not end_move:
            sumito = enemy in colors
            r, c = self.hexa_to_square(next)
            current_spot = self.board[r][c]

            if current_spot in (friend, enemy):  
                colors.append(self.board[r][c])
            
            # check if more than 3 marbles are being moved (forbidden)
            # or if a forbidden sumito is being performed (non-free spot after last enemy)
            too_much_marbles = colors.count(color) > 3
            wrong_sumito = colors.count(enemy) >= colors.count(friend)

            if too_much_marbles or wrong_sumito:
                if too_much_marbles:
                    err_messages("ERR_TOO_MUCH")
                else:
                    err_messages("ERR_SUMITO")                     
                self.ask_move(friend)
                return

            # if we keep finding our own marbles
            if current_spot == friend and (r, c) not in sequence.keys():
                sequence[(r, c)] = friend
            # we either find an enemy or an empty spot
            elif current_spot in (enemy, free):
                sequence[(r, c)] = enemy if sumito else friend
                # if its an actual free spot, we break the while loop
                if current_spot == free:
                    end_move = True
            else:
                if colors[-1] == enemy:
                    info_messages("GG_KILLED_ENEMY")
                    self.marbles[enemy] -= 1
                else:
                    info_messages("WARN_SUICIDE")
                    self.marbles[friend] -= 1
                end_move = True 
            
            # getting the next spot
            next_row = chr(ord(next[0]) + j)
            next_col = int(next[1]) + int(k)
            next = f"{next_row}{next_col}"


    def middle_marble(self, marbles_group, color):
        """
        TODO
        """
        marbles_group = sorted(marbles_group, key=lambda s: s[1])

        # getting the middle marble
        min_r = min(marbles_group, key=lambda s: ord(s[0]))[0]
        max_r = max(marbles_group, key=lambda s: ord(s[0]))[0]
        if min_r == max_r: 
            mid_row = min_r # case of horizontal range  
        else:
            mid_row = chr((ord(min_r) + ord(max_r)) // 2) # case of diagonal range

        min_c = min(marbles_group, key=lambda s: int(s[1]))[1]
        max_c = max(marbles_group, key=lambda s: int(s[1]))[1]
        if min_c == max_c:
            mid_col = min_c
        else:
            mid_col = str((int(min_c) + int(max_c)) // 2)
        return mid_row + mid_col

    def valid_neighborhood(self, first, color, enemy):
        """
        TODO
        """
        valid_neighborhood = []
        disp = [lambda r, c: (r - 1, c),
                lambda r, c: (r - 1, c - 1),
                lambda r, c: (r + 1, c + 1),
                lambda r, c: (r + 1, c)]
        
        r, c = self.hexa_to_square(first)
        for fun in disp:
            n_r, n_c = fun(r, c)
            if self.board[n_r][n_c] not in (color, enemy):
                valid_neighborhood.append((n_r, n_c))
        return valid_neighborhood
        
            
    def predict_direction(self, first, next):
        """
        TODO
        """
        # predicting the next rows
        if first[0] == next[0]: # lateral pushing
            j = 0
        else:
            # diagonal pushing direction (up: 1, down: -1)
            j = 1 if ord(first[0]) < ord(next[0]) else -1 

        # predicting the next columns
        if j == 0:
            k = 1 if first[1] < next[1] else -1
        else:
            k = 0 if first[1] == next[1] else -j 

        return j, k
                    

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
    B.ask_move(3)
    print(B)
    

if __name__ == "__main__": 
    main()
