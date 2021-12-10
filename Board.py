
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
    """
    A class used to represent a standard Abalone board.

    Static attributes
    ----------
    dimension: int
        Number of rows, columns of the board
    mid_point: int
        Middle row
    char_2_num: dict
        Dictionnary with key:value pairs string:int 
        such as "A":1, "B:2", etc.
        Used to convert coordinates.
    disp: dict
        Dictionnary with key:values pairs string:lambda function
        The key represents an orientation (i.e. "E" for East) and
        its associated value is a lambda function using 2 parameters.
        The dictionnary is used to compute new coordinates of a 
        given sport of the board
    
    Attributes
    ----------
    marbles: dict
        Dictionnary with key:values pairs int:int.
        The key represents a marbles color (i.e. 2 for red marbles,
        3 for green ones) and the associated value is the number
        of such marble still on the board.
        Both players start with an equal amount of 14 marbles.
    board: list
        Nested list (2 dimensional).
        Used to represent the board's state
        The list is filled with integer values such as:
        0: dead zone (if a marbles goes into it, it dies)
        1: empty spot
        2: red marble
        3: green marble

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    dimension = 9
    mid_point = math.floor(dimension / 2)
    char_2_num = {chr(ord("A") + i): i for i in range(9)}
    disp = {
        "E" : lambda r, c: (r, c + 1),
        "W" : lambda r, c: (r, c - 1),
        "NE": lambda r, c: (r - 1, c),
        "SW": lambda r, c: (r + 1, c),
        "NW": lambda r, c: (r - 1, c - 1),
        "SE": lambda r, c: (r + 1, c + 1),
    }

    def __init__(self):
        """
        TODO
        """
        self.marbles = {2: 14, 3: 14}

        # We assume the standard initial configuration commonly used
        # So its hard-coded
        self.board = [[2, 2, 2, 2, 2, 0, 0, 0, 0],
                      [2, 2, 2, 2, 2, 2, 0, 0, 0],
                      [1, 1, 2, 2, 2, 1, 1, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 3, 1, 1, 1, 1, 1],
                      [0, 0, 1, 1, 3, 3, 3, 1, 1],
                      [0, 0, 0, 3, 3, 3, 3, 3, 3],
                      [0, 0, 0, 0, 3, 3, 3, 3, 3]]

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
        data_user: tuple 
            The marble(s) the player wants to move
        orientation: string
            The orientation where the marble(s) are being moved
        """
        color_word = "Red" if color == 2 else "Green"
        print(colored(f"{color_word}, it's your turn!",
                      f"{color_word.lower()}",
                      attrs=["bold"]))
        print(self)

        valid_move = False
        while not valid_move:
            expr = r"^([A-Z][1-9]\s?){1,3}$"
            move = input("Pick your marble(s) (row-col: A-I, 0-8): ")
            if re.match(expr, move, re.IGNORECASE) is None:
                err_messages("ERR_INPUTS")
                continue
            user_data = tuple(sliced(move, 2))

            # check if the selection of multiple marbles is correct
            diagonal = self.is_diagonal(user_data)
            horizontal = self.is_horizontal(user_data)
            if len(user_data) > 1:
                if not diagonal and not horizontal:
                    err_messages("ERR_RANGE")
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

        # check if the orientation is correct
        ori = ["W", "E", "NW", "SE", "NE", "SW"]
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
        If the player gives more than one marble, then its a "free move".
        Otherwise, its a "push move", the marbles are being pushed.

        Parameters
        ----------
        user_data: tuple of strings (required)
            Inputs given by the user and describe its move
        color: int (required):
            Current player's color
        enemy: int (required)
            Current's player enemy

        Returns
        -------
        valid_update: bool
            It is possible that the player's move is incorrect.
            For instance, a wrong sumito cannot be taken in consideration.
            If valid_update is True, then the board is updated.
            Otherwise inputs are being asked again to the player.
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
        """
        TODO
        """
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
            print("element=", element)
            valid_neighbors = self.valid_neighborhood(element, 
                                                      friend,
                                                      enemy)
            print("neigh=", valid_neighbors)
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
        r, c = self.to_2d_list(marbles)
        for fun in Board.disp.values():
            n_r, n_c = fun(r, c)
            if self.board[n_r][n_c] not in (friend, enemy):
                valid_neighborhood.append((n_r, n_c))
        return valid_neighborhood

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
        r, g, c, y = "red", "green", "cyan", "yellow"

        j = 1
        k = Board.mid_point
        l = Board.dimension
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
        for i in range(Board.dimension):
            l_row = list(
                num_char[str(e)] if e != 0 else " "
                for e in self.board[i]
            )
            letter = colored(str(chr(65 + i)), c)  # chr(65) = "A"

            if i < Board.mid_point:
                str_to_add = f"{k * sp}{letter} {sp.join(l_row).rstrip()}"
                current_board.append(str_to_add)
                k -= 1
            elif i > Board.mid_point:
                str_to_add = f"{j * sp}{letter} {sp.join(l_row).lstrip()} "
                str_to_add += f"{colored(l, y)}"
                current_board.append(str_to_add)
                j += 1
                l -= 1
            else:
                current_board.append(f"{letter} {sp.join(l_row)}")
        return current_board

    def __str__(self):
        """Returns a full representation of the object as a string.
        
        Parameter
        ---------
        None
        
        Returns
        -------
        full_representation: string
            Orientations schematics and current board's state
        """
        orientations = colored("ORIENTATIONS", "white", attrs=["bold"])
        board = colored("BOARD", "white", attrs=["bold"])
        board_iter = iter(self.current_board_state())
        dead_zone = colored("DEAD ZONE:", "white", attrs=["bold"])
        dead_red = f"Red: {14 - self.marbles[2]}"
        dead_red = colored(dead_red, "red", attrs=["bold"])
        dead_green = f"Green: {14 - self.marbles[3]}"
        dead_green = colored(dead_green, "green", attrs=["bold"])
        r_numbers = " ".join(list(colored(str(e), "yellow")
                                  for e in range(1, 6)))

        full_representation = (
            f"""
          {orientations}                      {board}        {dead_zone}
                                |    {next(board_iter)}      {dead_red}
            NW     NE           |    {next(board_iter)}     {dead_green}
              \   /             |    {next(board_iter)}
               \ /              |    {next(board_iter)}
        W ----- 0 ----- E       |    {next(board_iter)}
               / \              |    {next(board_iter)}
              /   \             |    {next(board_iter)}
            SE     SW           |    {next(board_iter)}
                                |    {next(board_iter)}
                                |           {r_numbers}
        """
        )
        return full_representation

    @staticmethod
    def next_spot(r, c, orientation) -> tuple:
        """Compute the next spot of a given one.

        Parameters
        ----------
        r: int (positional)
            Row number of the given spot in the 2d-list frame
        c: int (positional)
            Column number of the given spot in the 2d-list frame
        orientation: string (positional)
            Orientation in which the next's spot is being computed

        Returns
        -------
        next spot: tuple of ints:
            new coordinates (row, col) in the 2d-list frame
        """
        next_spot = Board.disp[orientation](r, c)
        return next_spot

    @staticmethod
    def to_2d_list(user_data):
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
        n_r = Board.char_2_num[r]
        if c in (Board.mid_point, Board.mid_point + 1):
            n_c = int(c)
        else:
            n_c = int(c) + (ord(r) - ord("A")) - (Board.mid_point + 1)
        return n_r, n_c

    @staticmethod
    def enemy(color):
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
            
    @staticmethod
    def is_diagonal(user_data) -> bool:
        """Check if a range of marbles is aligned along a diagonal.
            
        Parameters
        ----------
        user_data: tuple (positional)
            Range of marbles given by the user
            
        Returns
        -------
        is_diagonal: bool
            True if the range is a diagonal, False otherwise
        """        
        min_r = min(user_data, key=lambda t: t[0])[0].upper()
        max_r = max(user_data, key=lambda t: t[0])[0].upper()
        is_diagonal = (
            len(set(e[1] for e in user_data)) == 1
            and ord(max_r) - ord(min_r) < len(user_data)
        )
        return is_diagonal

    @staticmethod
    def is_horizontal(self, user_data) -> bool:
        """Check if a range of marbles is aligned along a horizontal axis.
            
        Parameters
        ----------
        user_data: tuple (positional)
            Range of marbles given by the user
            
        Returns
        -------
        is_horizontal: bool
            True if the range is horizontal, False otherwise
        """
        min_c = min(user_data, key=lambda t: t[1])[1]
        max_c = max(user_data, key=lambda t: t[1])[1]
        is_horizontal = (
            len(set(e[0] for e in user_data)) == 1
            and int(max_c) - int(min_c) < len(user_data)
        )
        return is_horizontal


def main():
    game_is_on = True
    B = Board()
    color = random.choice((2, 3))
    game_over = False
    print(B)
    # while not game_over:
    #     user_data, orientation = B.ask_move(3)
    #     valid_move = B.update_board(user_data, orientation, 3)
    #     if not valid_move:
    #         continue


if __name__ == "__main__":
    main()


# def board_debug(self):
#     r, g, c, y = self.r, self.g, self.c, self.y

#     j = 1
#     k = self.middle
#     l = self.dimension
#     sp = " "  # space

#     # 0: f = forbidden spot
#     # 1: e = empty spot
#     # 2: w = white marble
#     # 3: b = black marble
#     num_char = {
#         "0": "f",
#         "1": colored("o", attrs=["bold"]),
#         "2": colored("#", r, attrs=["bold"]),  # ??
#         "3": colored("x", g, attrs=["bold"])  # ??
#     }

#     current_board = f"{7 *sp}SQUARE {21* sp} HEXA\n"  # first line
#     current_board = colored(current_board, attrs=["bold"])
#     for i in range(self.dimension):
#         l_row = list(
#             num_char[str(e)] if e != 0 else " "
#             for e in self.board[i]
#         )
#         current_board += f"{colored(i, c)} {sp.join(l_row)} {4 * sp}|   "
#         letter = colored(str(chr(65 + i)), c)  # chr(65) = "A"

#         if i < self.middle:
#             str_to_add = f"{k * sp}{letter} {sp.join(l_row).rstrip()}\n"
#             current_board += str_to_add
#             k -= 1
#         elif i > self.middle:
#             str_to_add = f"{j * sp}{letter} {sp.join(l_row).lstrip()}"
#             current_board += f"{str_to_add} {colored(l, y)}\n"
#             j += 1
#             l -= 1
#         else:
#             current_board += f"{letter} {sp.join(l_row)}\n"

#     # numbers bottom debug
#     l_number = list(
#         colored(str(e), y)
#         for e in range(0, 9)
#     )
#     # 13 to match the spaces
#     r_numbers = " ".join(list(
#         colored(str(e), y) for e in range(1, 6))
#     )
#     current_board += f"  {sp.join(l_number)} {13 * sp} {r_numbers}"

#     return current_board
