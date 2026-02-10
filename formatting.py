from constants import MAX_ATTEMPTS
from typing import List

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

def guesses_remaining_line(attempts_left: int, player_index: int) -> str:
    return f"\n{attempts_left} Guesses Remaining - Player {player_index}"

def render_feedback(correct_numbers: int, correct_locations: int) -> str:
    return f"{correct_numbers} correct numbers, {correct_locations} correct locations"

def render_guess_history(history: list[str]) -> str:
    return "\n".join(history)

def render_secret(secret: list[int]) -> str:
    return " ".join(str(d) for d in secret)

def ordinal(n: int) -> str:
    return ORDINALS.get(n)

def render_scoreboard_from_public_state(players: List[dict]) -> str:
    """
    Reproduce your domain scoreboard idea on the client:
    - solved first (sorted by attempts_left DESC, then index ASC)
    - unsolved after
    - rank increments when attempts_left changes among solvers
    """
    solved = [p for p in players if p.get("solved")]
    unsolved = [p for p in players if not p.get("solved")]

    solved.sort(key=lambda p: (-p.get("attempts_left", 0), p.get("index", 0)))
    unsolved.sort(key=lambda p: p.get("index", 0))

    lines = []
    rank = 0
    last_attempts = None

    for p in solved:
        attempts_left = p.get("attempts_left", 0)
        if last_attempts is None or attempts_left != last_attempts:
            rank = 1 if rank == 0 else rank + 1
            last_attempts = attempts_left
        lines.append(f"{rank}: Player {p['index']}")

    if unsolved:
        next_rank = 1 if rank == 0 else rank + 1
        for p in unsolved:
            lines.append(f"{next_rank}: Player {p['index']} (did not solve)")

    return "\n".join(lines)
