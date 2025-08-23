from typing import List, Tuple
import game as gm 


def show_scoreboard(players: List[gm.Player]) -> None:
    ranked: List[Tuple[int, gm.Player]] = gm.build_scoreboard(players)
    print("\n[SCOREBOARD]")
    for rank, p in ranked:
        tail = "" if p.solved else " (did not solve)"
        print(f"{rank}: Player {p.index}{tail}")


def demo_single_player():
    print("\nSINGLE PLAYER (live Random.org)")
    cfg = gm.build_game_config(mode="1", num_players=None, shared_choice=None, difficulty="1")
    state = gm.init_game(cfg)

    p = gm.current_player(state)
    print("Secret length:", len(p.secret))
    print("Attempts left:", p.attempts_left)
    print("secret:", p.secret)

    # Try a hint if allowed
    if gm.can_take_hint(p, cfg):
        print("Hint:", gm.give_hint(p, cfg))
    else:
        print("Hint not allowed (only 1 attempt left).")

    # Try an all zeros guess
    guess = [0] * cfg.length
    cn, cl, fb = gm.process_guess(p, guess)
    print("Guess:", guess, "->", fb, "| attempts_left:", p.attempts_left, "| solved:", p.solved)

    # try an all sevens guess
    if not p.solved:
        guess = [7] * cfg.length
        cn, cl, fb = gm.process_guess(p, guess)
        print("Guess:", guess, "->", fb, "| attempts_left:", p.attempts_left, "| solved:", p.solved)

    
    # Force a correct guess to test attempts_taken_to_solve to make sure it's working
    correct_guess = p.secret[:]  # exact match
    cn, cl, fb = gm.process_guess(p, correct_guess)
    print("Solved guess ->", fb)
    print("Attempts taken to solve:", p.attempts_taken_to_solve)

    show_scoreboard(state.players)


def demo_multiplayer_shared():
    print("\nMULTIPLAYER SHARED SECRET (live Random.org)")
    cfg = gm.build_game_config(mode="2", num_players=3, shared_choice="1", difficulty="1")
    state = gm.init_game(cfg)

    secrets = [pl.secret for pl in state.players]
    print("All secrets same? ->", all(s == secrets[0] for s in secrets))
    print("secrets:", secrets)

    # P1 guess all zeros
    p1 = gm.current_player(state)
    cn, cl, fb = gm.process_guess(p1, [0] * cfg.length)
    print(f"P1 guess -> {fb} | attempts_left: {p1.attempts_left}")
    gm.advance_turn(state)

    # P2 takes a hint (if allowed)
    p2 = gm.current_player(state)
    if gm.can_take_hint(p2, cfg):
        print("P2 hint:", gm.give_hint(p2, cfg))
    gm.advance_turn(state)

    # P3 guess all sevens
    p3 = gm.current_player(state)
    cn, cl, fb = gm.process_guess(p3, [7] * cfg.length)
    print(f"P3 guess -> {fb} | attempts_left: {p3.attempts_left}")

    show_scoreboard(state.players)


def demo_multiplayer_different():
    print("\nMULTIPLAYER DIFFERENT SECRETS (live Random.org)")
    cfg = gm.build_game_config(mode="2", num_players=2, shared_choice="2", difficulty="1")
    state = gm.init_game(cfg)

    s1, s2 = state.players[0].secret, state.players[1].secret
    print("P1 secret length:", len(s1), "| P2 secret length:", len(s2))

    # P1 random simple guess
    p1 = gm.current_player(state)
    cn, cl, fb = gm.process_guess(p1, [0] * cfg.length)
    print(f"P1 guess -> {fb} | attempts_left: {p1.attempts_left}")
    print("Before advance (should be 1 for P1):", gm.current_player(state).index)
    gm.advance_turn(state)
    print("After advance (should be 2 for P2):", gm.current_player(state).index)
    print("P1 attempts left:", p1.attempts_left)
    print("P1 history:", p1.history)
    print("P1 attempts taken to solve:", p1.attempts_taken_to_solve)

    # P2 hint then guess
    p2 = gm.current_player(state)
    if gm.can_take_hint(p2, cfg):
        print("P2 hint:", gm.give_hint(p2, cfg))
    cn, cl, fb = gm.process_guess(p2, [7] * cfg.length)
    print(f"P2 guess -> {fb} | attempts_left: {p2.attempts_left}")

    show_scoreboard(state.players)
    


def main():
    demo_single_player()
    demo_multiplayer_shared()
    demo_multiplayer_different()
    print("\nDone.")


if __name__ == "__main__":
    main()
