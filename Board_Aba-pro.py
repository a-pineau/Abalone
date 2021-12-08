
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
        "A": 0, "B": 1, "C": 2, "D": 3, "E": 4,
        "F": 5, "G": 6, "H": 7, "I": 8
    }

    def __init__(self):
        """Constructor.

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
        """Compute the current enemy of the current color.

        Parameter
        ---------
        color: int (positional)
            Current player's color

        Return
        ------
        enemy: int
            Current player's enemy

        """
        enemy: int = color + 1 if color == 2 else color - 1
        return enemy

    def ask_move(self, color):
        """Ask the current player his move.

        The player is asked until his input is valid.
        It first checks if the type of movement is correct (push or free).
        Then it checks if the positions entered can be updated.
        For instance, an empty or an enemy spot cannot be directly moved.
        Once the input is valid, the method update_board is called.

        Parameter
        ---------
        color: int (positional)
            Player's current color

        Returns
        -------
        None
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
                expr = r"^([A-Z][1-9]\s?){1,2}\s?([A-Z][1-9]){1}$"
                msg = ask_messages("ASK_F_MARBLES")
                       

            data_user = input(colored(msg, attrs=["bold"]))
            data_user = data_user.replace(" ", "")
            # check if the selection is correct
            if re.match(expr, data_user, re.IGNORECASE) is None:  
                err_messages("ERR_INPUTS")
                continue

            # pairs value construction
            data_user = tuple(sliced(data_user, 2))

            # pairs construction in the 2d list frame
            data_2d_array = (self.hexa_to_square(c) for c in data_user)
            data_2d_array = tuple(data_2d_array)

            # check if all the selected marbles have the same color
            values = tuple(self.board[r][c] for r, c in data_2d_array)
            if enemy in values:
                err_messages("ERR_WRONG_MARBLES")
                continue

            valid_move = True
        
        # board update
        self.update_board(data_user, move_type, color, enemy)

    def hexa_to_square(self, coords_hexa):
        """Converts coordinates of a given marble.

        Translates the coordinates of a given spot on the hexagonal
        board (i.e: "G3") into a valid row-column couple used by
        the 2d-list (self.board)

        Parameters
        ----------
        coords_hexa: string (positional)
            Coordinates of a given spot on the hexagonal board

        Returns
        -------
        n_r, n_c: tuple (int)
            Coordinates of the given spot in the 2d-list (self.board)
        """
        r, c = coords_hexa.upper()
        n_r = self.char_2_num[r]
        if c in (self.middle, self.middle + 1):
                n_c = int(c)
        else:
                n_c =int(c) + (ord(r) - ord("A")) - (self.middle + 1)
        return n_r, n_c


    def update_board(self, data_user, move_type, color, enemy):
        """Update the board with new values.

        This method is called after submitting a correct move.
        It initializes an empty dict and passes it to methods which
        will fill it. The method call depends on the player's move.
        
        Parameters
        ----------
        data_user: tuple of strings (required)
            Inputs given by the user and describe its move
        move_type: string (required)
            Current player's move ("P": pushing marbles, "F":
            free move)
        color: int (required):
            Current player's color
        enemy: int (required)
            Current's player enemy

        Returns
        -------
        None
        """
        enemy = color - 1 if color == 3 else color + 1
        sequence = dict()

        if move_type == "P":
            self.push_marbles(data_user, sequence, color, enemy)
        else:
            self.move_marbles(data_user, sequence, color, enemy)

        for key, value in sequence.items():
            row, col = key
            self.board[row][col] = value


    def move_marbles(self, data_user, sequence, color, enemy):
        """
        TODO        
        """
        friend = color 
        marbles_range, next_m = list(data_user[:-1]), data_user[-1]
        unique_marble: bool = len(marbles_range) == 1

        if not unique_marble:
            first_m, last = marbles_range
            # this will be used later on to predict the next positions
            j, k = self.predict_direction(marbles_range[0], 
                                          marbles_range[1])

            # lengths (rows, columns) of the range
            l_row = abs(ord(last[0]) - ord(first_m[0]))
            l_col = abs(int(last[1]) - int(first_m[1]))

            # the range cannot have more than 3 marbles
            if any(l > 2 for l in (l_row, l_col)):
                err_messages("ERR_RANGE")
                self.ask_move(color)
                return

            range_3_marbles = any(l == 2 for l in (l_row, l_col))

            # range of 3 marbles, we need to find the middle one
            # as the user provides w/ the first_m and the last marble
            if range_3_marbles:
                mid_marble = self.middle_marble(marbles_range, color)
                marbles_range.insert(1, mid_marble)

        # check if the range does not contain empty spots or enemies
        data_2d_array = (self.hexa_to_square(e) for e in marbles_range)
        if any(self.board[r][c] != friend for r, c in data_2d_array):
            err_messages("ERR_NON_FRIENDLY_RANGE")
            self.ask_move(color)
            return
            
        for element in marbles_range:
            valid_neighborhood = self.valid_neighborhood(element, 
                                                         color,
                                                         enemy)
            r, c = self.hexa_to_square(element)
            n_r, n_c = self.hexa_to_square(next_m)
            if (n_r, n_c) not in valid_neighborhood:
                err_messages("ERR_MOVE_RANGE")
                self.ask_move(color)
                return
            sequence[(r, c)] = 1
            sequence[(n_r, n_c)] = color

            if not unique_marble:
                # getting the next_m spot
                next_m_row = chr(ord(next_m[0]) + j)
                next_m_col = int(next_m[1]) + int(k)
                next_m = f"{next_m_row}{next_m_col}"

    def push_marbles(self, data_user, sequence, color, enemy):
        """Compute the new positions of marbles.

        This method is called whenever a player wants to move
        marbles by pushing them. It also checks if a sumito is 
        being performed and if a marble is being ejected.
        
        Parameters
        ----------
        data_user: tuple of strings (required)
            Inputs given by the user and describe its move
        sequence: dict (required)
            New positions of marbles
        color: int (required):
            Current player's color
        enemy: int (required)
            Current's player enemy

        Returns
        -------
        None
        """

        free = 1
        friend = color
        enemy = friend - 1 if friend == 3 else friend + 1 # current enemy
        first_m, next_m = data_user # the first_m marble and its next_m spot
        j, k = self.predict_direction(first_m, next_m)
        r, c = self.hexa_to_square(first_m) # coordinates in 2d-array

        sequence[(r, c)] = 1 # the first_m marble becomes an empty spot
        colors = [friend] # storing the colors we meet

        # we first_m check that the selected marble is correct 
        # it cannot be an enemy or an empty spot
        if self.board[r][c] != friend:
            err_messages("ERR_WRONG_MARBLES")
            self.ask_move(friend)
            return
    
        end_move = False # better readibilty than a while True
        while not end_move:
            sumito = enemy in colors
            r, c = self.hexa_to_square(next_m)
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
            
            # getting the next_m spot
            next_m_row = chr(ord(next_m[0]) + j)
            next_m_col = int(next_m[1]) + int(k)
            next_m = f"{next_m_row}{next_m_col}"


    def middle_marble(self, marbles_range, color):
        """Compute the middle spot of a given range of marbles

        For instance, the middle spot of the following range: "G3G5"
        will be "G4". It deals with both horizontal and diagonal ranges.
        This method is called whenever the player wants to freely move
        3 marbles.

        Parameter
        ---------
        marbles_ranges: list of strings (positional)
            Range of marbles
        
        Returns
        -------
        None
        """
        marbles_range = sorted(marbles_range, key=lambda s: s[1])

        # getting the middle marble
        min_r = min(marbles_range, key=lambda s: ord(s[0]))[0]
        max_r = max(marbles_range, key=lambda s: ord(s[0]))[0]
        if min_r == max_r: 
            mid_row = min_r # case of horizontal range  
        else:
            mid_row = chr((ord(min_r) + ord(max_r)) // 2) # case of diagonal range

        min_c = min(marbles_range, key=lambda s: int(s[1]))[1]
        max_c = max(marbles_range, key=lambda s: int(s[1]))[1]
        if min_c == max_c:
            mid_col = min_c
        else:
            mid_col = str((int(min_c) + int(max_c)) // 2)
        return mid_row + mid_col

    def valid_neighborhood(self, marble, color, enemy):
        """Compute where a given marble can move.

        Method called whenever the player wants to freely move marbles.
        It thus is called only if move_marbles is called
        A given marble can be moved into an empty spot or the dead
        zone (which corresponds to killing a own marble).
        
        Parameter
        ---------
        marble: string (positional)
            The marble the player wants to move
        color: int (positional)
            Player's current move
        enemy: int (positional)
            Player's current enemy

        Returns
        -------
        valid_neighborhood: list
            All the valid locations where the marble can be moved
        """
        valid_neighborhood = []
        disp = [lambda x, y: (x - 1, y),
                lambda x, y: (x - 1, y - 1),
                lambda x, y: (x + 1, y + 1),
                lambda x, y: (x + 1, y)]
        
        r, c = self.hexa_to_square(marble)
        for fun in disp:
            n_r, n_c = fun(r, c)
            if self.board[n_r][n_c] not in (color, enemy):
                valid_neighborhood.append((n_r, n_c))
        return valid_neighborhood
        
            
    def predict_direction(self, first_m, next_m):
        """
        TODO
        """
        # predicting the next rows
        if first_m[0] == next_m[0]: # lateral pushing
            j = 0
        else:
            # diagonal pushing direction (up: 1, down: -1)
            j = 1 if ord(first_m[0]) < ord(next_m[0]) else -1 

        # predicting the next columns
        if j == 0:
            k = 1 if first_m[1] < next_m[1] else -1
        else:
            k = 0 if first_m[1] == next_m[1] else -j 
        return j, k
                    

    def __str__(self):
        """Returns the current boards states.

        Two boards are displayed:
        Debug that corresponds to the 2D-list w/ the associated indexes
        Board shows the actual play board 

        Paremeters
        ----------
        None

        Returns 
        -------
        current_board: str
            Boards states
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

        current_board = f"{7 *sp}SQUARE {21* sp} HEXA\n" # first_m line
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
