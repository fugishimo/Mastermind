from constants import (
    DIFFICULTY_MAP, MSG_WELCOME, MSG_MODE_PROMPT, MSG_PLAYER_COUNT, MSG_SHARED_PROMPT,
    MSG_DIFFICULTY, MSG_TURN_PROMPT, MSG_INVALID_INPUT, MSG_ONE_LEFT_NO_HINT,
    MSG_NO_HINTS_LEFT, MSG_ALL_CORRECT, MSG_OUT_OF_GUESSES, MSG_PLAY_AGAIN,
    HISTORY, HINT, MIN_DIGITS, MAX_DIGITS
)
from models import GameState
from formatting import guesses_remaining_line, render_guess_history, render_scoreboard_from_public_state
import client_service
import requests
from typing import Optional

# ----------------------------
# Main
# ----------------------------

def main():
    while True:
        print(MSG_WELCOME)

        # Mode
        mode = input_until_valid({"1", "2"}, MSG_MODE_PROMPT)

        num_players = 1
        shared_choice: Optional[str] = None
        if mode == "2":
            num_players = int(input_players(MSG_PLAYER_COUNT))
            shared_choice = input_until_valid({"1", "2"}, MSG_SHARED_PROMPT)

        # Difficulty
        diff = input_until_valid(set(DIFFICULTY_MAP.keys()), MSG_DIFFICULTY)

        # Create game on backend (server generates secrets internally)
        created = safe_backend_call(
            client_service.create_game,
            mode=mode,
            difficulty=diff,
            num_players=num_players,
            shared_choice=shared_choice,
        )
        if not created:
            # failed to create; restart prompt loop
            continue

        game_id = created.get("game_id")
        if not game_id:
            print("\n[!] Backend response missing game_id.\n")
            continue

        # We'll fetch state for rendering / validation.
        state = safe_backend_call(client_service.get_game, game_id)
        if not state:
            continue

        length = state["length"]

        # Game loop: always drive via backend state
        while True:
            state = safe_backend_call(client_service.get_game, game_id)
            if not state:
                break

            if state.get("finished"):
                break

            current_player_index = state["current_player_index"]
            players = state["players"]
            p = next((x for x in players if x["index"] == current_player_index), None)

            if p is None:
                print("\n[!] Backend state missing current player.\n")
                break

            # If server advances automatically, this should rarely happen,
            # but we handle it by just refetching.
            if p.get("solved") or p.get("attempts_left", 0) == 0:
                continue

            print(guesses_remaining_line(p["attempts_left"], current_player_index))
            print(MSG_TURN_PROMPT)
            raw = input("> ").strip()

            # History
            if raw == HISTORY:
                history = p.get("history", [])
                print(render_guess_history(history) if history else "")
                continue

            # Hint
            if raw == HINT:
                if p.get("attempts_left", 0) == 1:
                    print(MSG_ONE_LEFT_NO_HINT)
                    continue

                cap = (length - 1) if num_players == 1 else 3
                if p.get("hints_used", 0) >= cap:
                    print("No hints remaining.")
                    continue

                hint_resp = safe_backend_call(client_service.take_hint, game_id)

                print(hint_resp.get("hint", ""))
                continue

            # Guess
            guess = parse_guess(raw, length)
            if guess is None or len(guess) != length or not all(MIN_DIGITS <= d <= MAX_DIGITS for d in guess):
                print(MSG_INVALID_INPUT)
                continue

            guess_resp = safe_backend_call(client_service.submit_guess, game_id, guess)
            if not guess_resp:
                continue

            print(guess_resp.get("feedback", ""))

            if guess_resp.get("solved"):
                print(MSG_ALL_CORRECT)

        # Finished → scoreboard
        final_state = safe_backend_call(client_service.get_game, game_id)
        if final_state:
            print("\nScoreboard:")
            print(render_scoreboard_from_public_state(final_state.get("players", [])))

            # NOTE: In a real client/server design, you do NOT reveal secrets to clients.
            # Your old CLI printed the secret on loss. Without a debug/admin endpoint,
            # the frontend should not be able to see it.

        again = input_until_valid({"1", "2"}, MSG_PLAY_AGAIN)
        if again == "2":
            break
        # else: loop back and create a new game


# ----------------------------
# Input Helpers
# ----------------------------

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
    

def safe_backend_call(fn, *args, **kwargs):
    """
    Wraps requests errors into friendly CLI output.
    """
    try:
        return fn(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        print("\n[!] Cannot connect to backend. Make sure the server is running:")
        print("    uvicorn api:app --reload\n")
        return None
    except requests.exceptions.HTTPError as e:
        # Try to show API-provided detail
        try:
            detail = e.response.json()
        except Exception:
            detail = e.response.text if e.response is not None else str(e)
        print(f"\n[!] Backend returned an error: {detail}\n")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n[!] Network error: {e}\n")
        return None

if __name__ == "__main__":
    main()
