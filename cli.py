from constants import (
    DIFFICULTY_MAP, MSG_WELCOME, MSG_MODE_PROMPT, MSG_PLAYER_COUNT, MSG_SHARED_PROMPT,
    MSG_DIFFICULTY, MSG_TURN_PROMPT, MSG_INVALID_INPUT, MSG_ONE_LEFT_NO_HINT,
    MSG_NO_HINTS_LEFT, MSG_ALL_CORRECT, MSG_OUT_OF_GUESSES, MSG_PLAY_AGAIN,
    HISTORY, HINT, MIN_DIGITS, MAX_DIGITS
)
from models import GameState
from game import (
    build_game_config, init_game, current_player, advance_turn, any_player_can_play,
    can_take_hint, give_hint, process_guess, build_scoreboard
)
from formatting import guesses_remaining_line, render_guess_history, render_scoreboard, render_secret

def main():
    while True:
        print(MSG_WELCOME)

        # Mode
        mode = input_until_valid({"1", "2"}, MSG_MODE_PROMPT)

        num_players = 1
        shared_choice = None
        if mode == "2":
            num_players = int(input_players(MSG_PLAYER_COUNT))
            shared_choice = input_until_valid({"1", "2"}, MSG_SHARED_PROMPT)

        # Difficulty
        diff = input_until_valid(set(DIFFICULTY_MAP.keys()), MSG_DIFFICULTY)

        # Build/init
        cfg = build_game_config(mode, num_players, shared_choice, diff)
        state: GameState = init_game(cfg)

        # Game loop
        while not state.finished:
            p = current_player(state)
            if p.solved or p.attempts_left == 0:
                advance_turn(state)
                if state.finished:
                    break
                continue

            print(guesses_remaining_line(p))
            print(MSG_TURN_PROMPT)
            raw = input("> ").strip()

            # History
            if raw == HISTORY:
                print(render_guess_history(p.history) if p.history else "")
                continue

            # Hint
            if raw == HINT:
                if p.attempts_left == 1:
                    print(MSG_ONE_LEFT_NO_HINT)
                    continue
                if not can_take_hint(p, cfg):
                    print(MSG_NO_HINTS_LEFT)
                    continue
                hint_text = give_hint(p, cfg)
                print(hint_text)
                continue

            # Guess
            guess = parse_guess(raw, cfg.length)
            if guess is None or len(guess) != cfg.length or not all(MIN_DIGITS <= d <= MAX_DIGITS for d in guess):
                print(MSG_INVALID_INPUT)
                continue

            correct_numbers, correct_locations, feedback = process_guess(p, guess)
            print(feedback)
            if p.solved:
                print(MSG_ALL_CORRECT)

            if not any_player_can_play(state):
                state.finished = True
            else:
                advance_turn(state)

        # Finished → scoreboard + reveals
        ranked = build_scoreboard(state.players)
        print("\nScoreboard:")
        print(render_scoreboard(ranked))

        if cfg.num_players == 1:
            player = state.players[0]
            if not player.solved:
                print(MSG_OUT_OF_GUESSES.format(secret=render_secret(player.secret)))
        else:
            for _, pl in ranked:
                if not pl.solved:
                    print(f"Player {pl.index} did not solve. The correct sequence was: {render_secret(pl.secret)}")

        again = input_until_valid({"1", "2"}, MSG_PLAY_AGAIN)
        if again == "2":
            break
        # else: full reset

# input helpers

def input_until_valid(valid_set: set[str], prompt: str) -> str:
    while True:
        print(prompt)
        s = input("> ").strip()
        if s in valid_set:
            return s
        print(MSG_INVALID_INPUT)

def input_players(prompt: str) -> str:
    while True:
        print(prompt)
        s = input("> ").strip()
        if s.isdigit():
            n = int(s)
            if 1 <= n <= 4:
                return s
        print(MSG_INVALID_INPUT)

def parse_guess(raw: str, length: int):
    parts = raw.split()
    if len(parts) != length:
        return None
    try:
        return [int(x) for x in parts]
    except ValueError:
        return None

if __name__ == "__main__":
    main()
