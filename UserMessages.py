# ---------------------- #
#     Error Messages     #
# ---------------------- #
from termcolor import colored


def user_messages(msg):
    messages = {
        "ERR_MOVEMENT": colored(
            "Invalid movement!",
            "red",
            attrs=["bold"]
        ),
        "ERR_INPUTS": colored(
            "Invalid inputs!", 
            "red", 
            attrs=["bold"]
        ),
        "ERR_MULTIPLE_MARBLES": colored(
            "You gotta select 3 linked marbles along a common axis!",
            "red",
            attrs=["bold"]
        ),
        "ERR_WRONG_MARBLES": colored(
            "You gotta chose your own marble(s)!",
            "red",
            attrs=["bold"]
        ),
        "ERR_ORIENTATION": colored(
            "Invalid orientation!",
            "red",
            attrs=["bold"]
        ),
        "ERR_MOVE_MULTIPLE": colored(
            "You cannot move your multiple marbles like this!",
            "red",
            attrs=["bold"]
        ),
        "ERR_TOO_MUCH": colored(
            "You cannot move more than 3 marbles!",
            "red",
            attrs=["bold"]
        ),
        "ERR_SUMITO": colored(
            "Wrong sumito!",
            "red",
            attrs=["bold"]
        ),
        "WARN_SUICIDE": colored(
            "You killed your own marble, GGs.",
            "yellow",
            attrs=["bold"]
        ),
        "GG_KILLED_ENEMY": colored(
            "You've killed an enemy marble!",
            "green",
            attrs=["bold"]
        )
    }
    print(messages[msg])


    if __name__ == "__main__":
        pass # test

