import pytest
import sys
sys.path.insert(0, "/home/adrian/Desktop/Python/Abalone/src")

from Board import Board

# testing Board.next_stop(r, c, orientation)
# ------------------------------------------
@pytest.mark.parametrize("orientation, expected_result", [
    ("E", (8, 6)),
    ("W", (8, 4)),
    ("NE", (7, 5)),
    ("NW", (7, 4)),
    ("SE", (9 ,6)),
    ("SW", (9, 5)),
])
def test_next_spot(orientation, expected_result):
    tB = Board()
    r, c = 8, 5
    msg = f"Error with {orientation}"
    assert tB.next_spot(r, c, orientation) == expected_result, f"{msg}"

# testing Board.to_2d_list(user_data)
# -----------------------------------
@pytest.mark.parametrize("user_data, expected_result", 
[
    ("G5", (7, 7)),
    ("A7", (1, 3)),
    ("F8", (6, 9)),
])
def test_to_2d_list(user_data, expected_result):
    tB = Board()
    msg = f"Error with {user_data}"
    assert tB.to_2d_list(user_data) == expected_result, f"{msg}"

# testing Board.push_move(friend, user_data, orientation, new_data)
# -----------------------------------------------------------------
new_data_i1_nw = { # correct push move - no sumito
    (9, 5): 1, 
    (8, 4): 3, 
    (7, 3): 3, 
}
new_data_a7_e = { # correct push move - suicide
    (1, 3): 1,
    (1, 4): 2,
    (1, 5): 2,
}
new_data_i3_nw = { # correct push move - with sumito
    (9, 7): 1,
    (8, 6): 3,
    (7, 5) :3,
    (6, 4): 3,
    (5, 3): 2,
    (4, 2): 2,
}
new_data_i2_nw = { # wrong push move - incorrect sumito (nb enemy > nb friend)
    # empty dict: could not be filled
}
new_data_h4_nw = { # wrong push_move - incorrect sumito (friend blocking)
    # empty dict: could not be filled 
}

@pytest.mark.parametrize("friend, user_data, orientation, expected_result", 
[
    (3, ("I1",), "NW", new_data_i1_nw),
    (2, ("A7",), "E", new_data_a7_e),
    (3, ("I3",), "NW", new_data_i3_nw),
    (3, ("I2",), "NW", new_data_i2_nw),
    (3, ("H4",), "NW", new_data_h4_nw),
])
def test_push_move(friend, user_data, orientation, expected_result):
    tB = Board()
    tB.board = tB.set_test_board()
    tB.board[6][4] = 2
    tB.board[5][3] = 2
    tB.board[7][4] = 2
    tB.board[6][3] = 2
    tB.board[6][3] = 2
    tB.board[6][5] = 2
    tB.board[5][4] = 3
    msg = f"Error with: {user_data}, {orientation}"
    assert tB.push_move(friend, user_data, orientation) == expected_result

# testing Board.free_move(friend, user_data, orientation, new_data)
# -----------------------------------------------------------------
new_data_c5c6c7_se = { # correct free move - 3 marbles moving to empty spots
    (3, 3): 1,
    (4, 4): 2,
    (3, 4): 1,
    (4, 5): 2,
    (3, 5): 1,
    (4, 6): 2,
}
new_data_g4g5_nw = { # wrong free move - 1 marble moving to a non-empty spot
    # empty dict: could not be filled
}

@pytest.mark.parametrize("friend, user_data, orientation, expected_result", 
[
    (2, ("C5", "C6", "C7",), "SE", new_data_c5c6c7_se),
    (3, ("G4", "G5",), "NW", new_data_g4g5_nw),
])
def test_free_move(friend, user_data, orientation, expected_result):
    tB = Board()
    tB.board = tB.set_test_board()
    tB.board[6][4] = 2
    tB.board[5][3] = 2
    tB.board[7][4] = 2
    tB.board[6][3] = 2
    tB.board[6][3] = 2
    tB.board[6][5] = 2
    tB.board[5][4] = 3
    msg = f"Error with: {user_data}, {orientation}"
    assert tB.free_move(friend, user_data, orientation) == expected_result