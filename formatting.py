from constants import MAX_ATTEMPTS
from models import Player

ORDINALS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
}

def guesses_remaining_line(player) -> str:
    if player is None:
        return f"{MAX_ATTEMPTS} Guesses Remaining"
    return f"\n{player.attempts_left} Guesses Remaining - Player {player.index}"

def render_feedback(correct_numbers: int, correct_locations: int) -> str:
    return f"{correct_numbers} correct numbers, {correct_locations} correct locations"

def render_guess_history(history: list[str]) -> str:
    return "\n".join(history)

def render_secret(secret: list[int]) -> str:
    return " ".join(str(d) for d in secret)

def ordinal(n: int) -> str:
    return ORDINALS.get(n)

def render_scoreboard(ranked: list[tuple[int, "Player"]]) -> str:
    lines = []
    for rank, p in ranked:
        if p.solved:
            suffix = ""
        else:
            suffix = " (did not solve)"
        lines.append(f"{rank}: Player {p.index}{suffix}")
    return "\n".join(lines)
