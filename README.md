Linkedin Mastermind Project 
By: Nicholas Aguirre

Mastermind Summary:

A command-line take on the classic Mastermind. The computer gets a secret sequence of digits fetched from Random.org (true randomness). Players have 10 attempts to crack the code, with standardized feedback after each guess.

Core Features:
True RNG: Secrets come from Random.org (0–7, duplicates allowed).



Difficulties:
* Depending on the mode, the random number sequence can either be the normal 4 digits, or can be increased to 6 (medium) or 8 (hard) digits. 
Normal = 4 digits
Medium = 6 digits
Hard = 8 digits



Modes:
Single Player (Has to guess a random number sequence)

Multiplayer (up to 4 players)
* Shared secret (all guess the same random number sequence like in first player mode)
* Different secrets (each player gets their own unique random number sequence)



How It Works:
Attempts: Each player gets 10 guesses.

Input: Enter digits separated by spaces (must match the chosen difficulty length).

Commands:
"#" → show only your guess history with feedback (In multiplayer mode only the players whose turn it is will be shown)

"?" → request a hint (Reveals one correct digit in its correct position)

Hints:
Cost 1 attempt; blocked if only 1 attempt remains

Single player: up to length of secret unique position hints
Multiplayer (shared or different secrets): max 3 hints per player (unique positions)

* If a player only has one guess left that he can attempt to guess the sequence, you will not be able to use a hint because a hint uses up a guess.

Feedback format (never reveals positions directly):
X correct numbers, Y correct locations

correct locations = exact matches (right digit, right position)
correct numbers = total count of guessed digits that appear anywhere in the secret, including those in the right spot (duplicate-safe: never count a digit more times than it appears in the secret).



How scoring works for the Feedback loop:
* The game scores each guess in two passes

Correct locations
* Count how many digits are exactly right and in the right spot.

Correct numbers (wrong spot)
* Add the numbers from the correct locations to this total number
* From the leftovers, count how many guessed digits also appear in the secret—but never more times than the secret has them.

Example with duplicates
Secret: 1 1 2 3
Guess: 1 2 1 1

Pass 1 — Correct locations
Only the first 1 lines up → 1

Pass 2 — Correct numbers (total, duplicate-safe)
Count how many times each digit appears in the secret and in the guess.
For each digit, take the smaller of those two numbers. Add them up.

Example: Secret = 1 1 2 3, Guess = 1 2 1 1

1s: secret has 2, guess has 3 → count 2
2s: secret has 1, guess has 1 → count 1
3s: secret has 1, guess has 0 → count 0

correct numbers = 2 + 1 + 0 = 3
(This total already includes any digits that were in the correct location.)

correct locations = 1

Feedback shown: 3 correct numbers, 1 correct locations



End of Game:
Win: Immediately prints "All correct! You win!" and you’re done.

Single-player loss: Reveals the secret:
Out of guesses! The correct sequence was: {secret}

Multiplayer:
Players who solve the sequence stop taking turns; others continue.

Scoreboard ranks by fewest personal turns to solve (ties share rank number).

Non-solvers are listed last and see their secret revealed:
Player X did not solve. The correct sequence was: {secret}

Replay: Prompt to start a fresh game (mode, players, and difficulty reset).