
# -------------------- #
#    Abalone Board     #
# -------------------- #
import math
import re
import itertools
import random

from more_itertools import sliced
from termcolor import colored
from UserMessages import ask_messages, err_messages, info_messages


class Board():

    r = "red"
    g = "green"
    c = "cyan"
    y = "yellow"
    char_2_num = {chr(ord("A") + i): i for i in range(9)}

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
                      [2, 1, 2, 2, 2, 1, 1, 0, 0],
                      [1, 3, 1, 1, 1, 1, 1, 1, 0],
                      [1, 1, 3, 1, 1, 1, 2, 1, 1],
                      [0, 3, 1, 1, 1, 1, 2, 1, 1],
                      [0, 0, 2, 1, 3, 3, 3, 1, 1],
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

    def ask_move(self, color) -> tuple:
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
        color_word = "Red" if color == 2 else "Green"
        print(colored(f"{color_word}, it's your turn!",
                      f"{color_word.lower()}",
                      attrs=["bold"]))
        print(self.board_debug())

        valid_move = False
        while not valid_move:
            expr = r"^([A-Z][1-9]\s?){1,3}$"
            move = input("Pick your marble(s) (row-col: A-I, 0-8): ")
            if re.match(expr, move, re.IGNORECASE) is None:
                err_messages("ERR_INPUTS")
                continue
            user_data = tuple(sliced(move, 2))

            # check if the selection of multiple marbles is correct
            if len(user_data) > 1:
                if (not self.is_diagonal(user_data) and
                    not self.is_horizontal(user_data)
                    ):
                    err_messages("ERR_MULTIPLE_MARBLES")
                    continue

            # pairs construction in the 2d list frame
            data_2d_list = (self.to_2d_list(c) for c in user_data)
            data_2d_list = tuple(data_2d_list)

            # check if all the selected marbles have the same color
            values = tuple(self.board[r][c] for r, c in data_2d_list)
            if not all(e == color for e in values):
                err_messages("ERR_WRONG_MARBLES")
                continue
            valid_move = True

        # the orientations are restricted if multiple marbles
        ori = ["W", "E", "NW", "SE"]
        if len(user_data) == 1:
            ori.extend(["NE", "SW"])  # otherwise we consider all of them

        # check if the orientation is correct
        valid_orientation = False
        while not valid_orientation:
            sep = ", "
            orientation = input(f"Orientation ({sep.join(ori)})?: ").upper()
            if orientation.upper() not in ori:
                err_messages("ERR_ORIENTATION")
                continue
            valid_orientation = True

        return user_data, orientation

    def update_board(self, user_data, orientation, color) -> bool:
        """Update the board with new values.

        This method is called after submitting a correct move.
        It initializes an empty dict and passes it to methods which
        will fill it. The method call depends on the player's move.

        Parameters
        ----------
        user_data: tuple of strings (required)
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
        new_data = dict()

        if len(user_data) > 1:
            valid_update = self.free_move(color,
                                          user_data,
                                          orientation,
                                          new_data)
        else:
            valid_update = self.push_move(color,
                                          user_data,
                                          orientation,
                                          new_data)

        # Updating board
        if valid_update:
            for key, value in new_data.items():
                row, col = key
                self.board[row][col] = value
        return valid_update

    def push_move(self, friend, user_data, orientation, new_data):
        empty = 1
        enemy = self.enemy(friend)
        r, c = self.to_2d_list(user_data[0])
        new_data[(r, c)] = 1  # the first marble becomes empty
        colors = [self.board[r][c]]

        while self.board[r][c] != empty:
            n_r, n_c = self.next_spot(r, c, orientation)
            current_spot = self.board[r][c]
            next_spot = self.board[n_r][n_c]
            colors.append(next_spot)

            sumito = enemy in colors
            too_much_marbles = colors.count(friend) > 3
            wrong_sumito = colors.count(enemy) >= colors.count(friend)

            # cannot push more than 3 marbles
            if too_much_marbles:
                err_messages("ERR_TOO_MUCH")
                return False
            # next spot is always friendly, except deadzone
            if current_spot == friend:
                if next_spot in (friend, enemy, empty):
                    new_data[(n_r, n_c)] = friend
                else:
                    # friend pushed to deadzone
                    info_messages("INFO_SUICIDE")
                    break
            # next spot depends on the sumito
            elif current_spot == enemy:
                if next_spot in (enemy, empty):
                    new_data[(n_r, n_c)] = enemy if sumito else enemy
                elif next_spot == friend:
                    wrong_sumito = True
                else:
                    # enemy pushed to deadzone
                    info_messages("INFO_KILL_ENEMY")
                    break

            # performing a wrong sumito
            if wrong_sumito:
                err_messages("ERR_SUMITO")
                return False

            r, c = n_r, n_c

        return True

    def free_move(self, friend, user_data, orientation, new_data) -> bool:
        """
        TODO

        """
        print(user_data)
        enemy = self.enemy(friend)
        for element in user_data:
            valid_neighbors = self.valid_neighborhood(element, 
                                                      friend,
                                                      enemy)
            r, c = self.to_2d_list(element)
            n_r, n_c = self.next_spot(r, c, orientation)
            if (n_r, n_c) not in valid_neighbors:
                err_messages("ERR_EMPTY_SPOT")
                return False
            new_data[(r, c)] = 1
            new_data[(n_r, n_c)] = friend

        return True

    def valid_neighborhood(self, marbles, friend, enemy) -> list:
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
            
        r, c = self.to_2d_list(marbles)
        for fun in disp:
            n_r, n_c = fun(r, c)
            if self.board[n_r][n_c] not in (friend, enemy):
                valid_neighborhood.append((n_r, n_c))
        return valid_neighborhood

    def to_2d_list(self, user_data):
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
        r, c = user_data.upper()
        n_r = self.char_2_num[r]
        if c in (self.middle, self.middle + 1):
            n_c = int(c)
        else:
            n_c = int(c) + (ord(r) - ord("A")) - (self.middle + 1)
        return n_r, n_c

    def is_diagonal(self, user_data):
        """
        TODO
        """
        min_r = min(user_data, key=lambda t: t[0])[0].upper()
        max_r = max(user_data, key=lambda t: t[0])[0].upper()
        return (
            len(set(e[1] for e in user_data)) == 1
            and ord(max_r) - ord(min_r) < len(user_data)
        )

    def is_horizontal(self, user_data):
        """
        TODO
        """
        # test along a horizontal line
        min_c = min(user_data, key=lambda t: t[1])[1]
        max_c = max(user_data, key=lambda t: t[1])[1]
        return (
            len(set(e[0] for e in user_data)) == 1
            and int(max_c) - int(min_c) < len(user_data)
        )

    def next_spot(self, r, c, orientation):
        """
        TODO
        """
        disp = {
            "NE": lambda r, c: (r - 1, c),
            "NW": lambda r, c: (r - 1, c - 1),
            "SE": lambda r, c: (r + 1, c + 1),
            "SW": lambda r, c: (r + 1, c),
            "E": lambda r, c: (r, c + 1),
            "W": lambda r, c: (r, c - 1),
        }
        return disp[orientation](r, c)

    def current_board_state(self):
        """Returns a view of the current board state.

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
        sp = " "

        # 0: f = forbidden spot
        # 1: e = empty spot
        # 2: w = white marble
        # 3: b = black marble
        num_char = {
            "0": "f",
            "1": colored("o", attrs=["bold"]),
            "2": colored("#", r, attrs=["bold"]),
            "3": colored("x", g, attrs=["bold"])
        }

        current_board = []
        for i in range(self.dimension):
            l_row = list(
                num_char[str(e)] if e != 0 else " "
                for e in self.board[i]
            )
            letter = colored(str(chr(65 + i)), c)  # chr(65) = "A"

            if i < self.middle:
                str_to_add = f"{k * sp}{letter} {sp.join(l_row).rstrip()}"
                current_board.append(str_to_add)
                k -= 1
            elif i > self.middle:
                str_to_add = f"{j * sp}{letter} {sp.join(l_row).lstrip()} "
                str_to_add += f"{colored(l, y)}"
                current_board.append(str_to_add)
                j += 1
                l -= 1
            else:
                current_board.append(f"{letter} {sp.join(l_row)}")
        return current_board

    def __str__(self):
        """
        TODO
        """
        orientations = colored("ORIENTATIONS", attrs=["bold"])
        board = colored("BOARD", attrs=["bold"])
        r_numbers = " ".join(list(colored(str(e), self.y)
                                  for e in range(1, 6)))
        board_iter = iter(self.current_board_state())
        full_representation = (
            f"""
          {orientations}                        {board}
                                |      {next(board_iter)}
            NW     NE           |      {next(board_iter)}
              \   /             |      {next(board_iter)}
               \ /              |      {next(board_iter)}
        W ----- 0 ----- E       |      {next(board_iter)}
               / \              |      {next(board_iter)}
              /   \             |      {next(board_iter)}
            SE     SW           |      {next(board_iter)}
                                |      {next(board_iter)}
                                |             {r_numbers}
        """
        )
        return full_representation

    def board_debug(self):
        r, g, c, y = self.r, self.g, self.c, self.y

        j = 1
        k = self.middle
        l = self.dimension
        sp = " "  # space

        # 0: f = forbidden spot
        # 1: e = empty spot
        # 2: w = white marble
        # 3: b = black marble
        num_char = {
            "0": "f",
            "1": colored("o", attrs=["bold"]),
            "2": colored("#", r, attrs=["bold"]),  # ??
            "3": colored("x", g, attrs=["bold"])  # ??
        }

        current_board = f"{7 *sp}SQUARE {21* sp} HEXA\n"  # first line
        current_board = colored(current_board, attrs=["bold"])
        for i in range(self.dimension):
            l_row = list(
                num_char[str(e)] if e != 0 else " "
                for e in self.board[i]
            )
            current_board += f"{colored(i, c)} {sp.join(l_row)} {4 * sp}|   "
            letter = colored(str(chr(65 + i)), c)  # chr(65) = "A"

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
    game_is_on = True
    B = Board()
    color = random.choice((2, 3))
    game_over = False
    while not game_over:
        user_data, orientation = B.ask_move(3)
        valid_move = B.update_board(user_data, orientation, 3)
        if not valid_move:
            continue


if __name__ == "__main__":
    main()
