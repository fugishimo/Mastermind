from formatting import (
    guesses_remaining_line,
    render_feedback,
    render_guess_history,
    render_secret,
    ordinal,
    render_scoreboard,
)
from models import Player
from constants import MAX_ATTEMPTS


def main():
    print("guesses_remaining_line")
    print(guesses_remaining_line(None))  # single-player
    p1 = Player(index=1, secret=[1, 2, 3, 4], attempts_left=7)
    print(guesses_remaining_line(p1))

    print("\nrender_feedback")
    print(render_feedback(3, 1))
    print(render_feedback(0, 0))

    print("\nrender_guess_history")
    history = [
        "1: 0 1 2 3 → 3 correct numbers, 1 correct locations",
        "2: 4 5 6 7 → 0 correct numbers, 0 correct locations",
    ]
    print(render_guess_history(history))

    print("\nrender_secret")
    print(render_secret([1, 5, 7, 3]))

    print("\nordinal")
    for n in [1, 2, 3, 4, 8, 9, 21]:
        print(n, "→", ordinal(n))

    print("\nrender_scoreboard")
    ranked = [
        (1, Player(index=2, secret=[], attempts_left=0, solved=True)),
        (2, Player(index=1, secret=[], attempts_left=0, solved=False)),
    ]
    print(render_scoreboard(ranked))


if __name__ == "__main__":
    main()
