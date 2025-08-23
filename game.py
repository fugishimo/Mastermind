from typing import List
from models import GameConfig, Player, RoundState, GameState
from constants import DIFFICULTY_MAP, MAX_ATTEMPTS
from random_org import fetch_secret
from score import score_guess
from formatting import render_feedback, ordinal

# ---- Build config/state ----

def build_game_config(mode: str, num_players: int | None, shared_choice: str | None, difficulty: str) -> GameConfig:
    length = DIFFICULTY_MAP[difficulty]
    attempts = MAX_ATTEMPTS
    shared_secret = (mode == "2" and shared_choice == "1")
    return GameConfig(length=length, attempts=attempts, shared_secret=shared_secret, num_players=(num_players or 1))

def create_players(cfg: GameConfig) -> List[Player]:
    players: List[Player] = []
    if cfg.num_players == 1:
        secret = fetch_secret(cfg.length)
        players.append(Player(index=1, secret=secret, attempts_left=cfg.attempts))
        return players

    if cfg.shared_secret:
        shared = fetch_secret(cfg.length)
        for i in range(cfg.num_players):
            players.append(Player(index=i + 1, secret=shared[:], attempts_left=cfg.attempts))
    else:
        for i in range(cfg.num_players):
            players.append(Player(index=i + 1, secret=fetch_secret(cfg.length), attempts_left=cfg.attempts))
    return players

def init_game(cfg: GameConfig) -> GameState:
    players = create_players(cfg)
    return GameState(config=cfg, players=players, round_state=RoundState(current_player_idx=0), finished=False)

# ---- Turn helpers ----

def current_player(state: GameState) -> Player:
    return state.players[state.round_state.current_player_idx]

def advance_turn(state: GameState) -> None:
    n = len(state.players)
    for _ in range(n):
        state.round_state.current_player_idx = (state.round_state.current_player_idx + 1) % n
        p = state.players[state.round_state.current_player_idx]
        if (not p.solved) and p.attempts_left > 0:
            return
    state.finished = True

def any_player_can_play(state: GameState) -> bool:
    return any((not p.solved and p.attempts_left > 0) for p in state.players)

# ---- Hints ----

def hint_cap(cfg: GameConfig) -> int:
    return cfg.length if cfg.num_players == 1 else 3

def can_take_hint(p: Player, cfg: GameConfig) -> bool:
    if p.attempts_left <= 1:
        return False
    cap = hint_cap(cfg)
    return p.hints_used < cap and len(p.hinted_positions) < cfg.length

def give_hint(p: Player, cfg: GameConfig) -> str:
    # reveal the first unhinted position
    for pos in range(cfg.length):
        if pos not in p.hinted_positions:
            p.hinted_positions.add(pos)
            p.hints_used += 1
            p.attempts_left -= 1
            digit = p.secret[pos]
            return f"{digit} is in {ordinal(pos + 1)} position"
    return "No hints remaining. Please enter your guess."

# ---- Guess processing ----

def process_guess(p: Player, guess: List[int]) -> tuple[int, int, str]:
    correct_numbers, correct_locations = score_guess(p.secret, guess)
    feedback = render_feedback(correct_numbers, correct_locations)

    # Append to history (one line per guess)
    line_num = len(p.history) + 1
    rendered_guess = " ".join(str(d) for d in guess)
    p.history.append(f"{line_num}: {rendered_guess} \u2192 {feedback}")

    # Spend an attempt for the guess
    p.attempts_left -= 1

    # Win condition: all positions correct
    if correct_locations == len(p.secret):
        p.solved = True
        # store personal number of guesses taken to solve (includes this guess)
        p.attempts_taken_to_solve = line_num

    return (correct_numbers, correct_locations, feedback)

# ---- Scoreboard ----

def build_scoreboard(players: List[Player]) -> List[tuple[int, Player]]:
    # Rank solvers by attempts_taken_to_solve (ascending); tie → same rank number.
    solved = [p for p in players if p.solved]
    unsolved = [p for p in players if not p.solved]

    solved.sort(key=lambda p: (p.attempts_taken_to_solve, p.index))

    ranked: List[tuple[int, Player]] = []
    rank = 0
    last_attempts = None
    for p in solved:
        if last_attempts is None or p.attempts_taken_to_solve != last_attempts:
            rank = (rank + 1) if rank > 0 else 1
            last_attempts = p.attempts_taken_to_solve
        ranked.append((rank, p))

    if unsolved:
        next_rank = (rank + 1) if rank > 0 else 1
        for p in unsolved:
            ranked.append((next_rank, p))

    return ranked
