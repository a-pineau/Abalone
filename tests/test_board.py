import pytest
import sys
sys.path.insert(0, "/home/adrian/Desktop/Python/Abalone/src")

from Board import Board

# testing Board.next_stop(r, c, orientation)
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
@pytest.mark.parametrize("user_data, expected_result", [
    ("G5", (7, 7)),
    ("A7", (1, 3)),
    ("F8", (6, 9)),
])
def test_to_2d_list(user_data, expected_result):
    tB = Board()
    msg = f"Error with {user_data}"
    assert tB.to_2d_list(user_data) == expected_result, f"{msg}"

# testing Board.push_move(friend, user_data, orientation, new_data)

