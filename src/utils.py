"""
    Utilities functions
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Player, Highscore


def validate_user_name(instance=None, attribute=None, value: str | None = None):
    """
    Validtor function to validate username
    """
    if not re.match("^[a-zA-z0-9_-]+$", value):
        return False
    return True


def compute_high_score(player: Player, high_score: Highscore) -> bool:
    """
    Checks if the current player score is higher than the current high score and if it is saves the new sore
    """
    if high_score.curent_high_score > player.points:
        high_score.insert(player=player)
    return True
