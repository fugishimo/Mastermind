# Thoughts during development

(8/20/2025)
## Initial thoughts

- After reading the pdf of the game, I didn't want to dive right into it. I wanted to thoroughly think about the different components 
for a unique game that I wanted to create.

## Gameplay
- I started by asking myself:
  - How do I want the game played?
  - Do I just want it to be a single player mode or be able to include
    multiple people?
  - Should there be different difficulty levels?
  - Should I put a limit to the amount of players that are playing?
  - What happens when someone inputs the wrong message?
  - Does the game just end when I win or lose?
  - How am I going to track the location of a number that's correct and count the number of numbers that are correct?
  - If there's a multiplayer mode should the players be able to choose if they want to have the same random sequence as the others
  or should it be unique to each player?
  - For Hints I had several questions:
    - How do I want the hints to work? 
    - Should I give them unlimited hints or limit it to a certain number?
    - How should the hint even work?
    - Should I give them a specific location of a number, or just a number thats in the sequence with no location?
    - Should a hint count as a "turn" and remove an attempt from your current guess count?
  - For multiplayer mode I had several questions:
    - How should I keep track of who is winning?
    - If they are playing the multiplayer mode and choose to have a shared random number sequence how will the winner be decided?
      - Should I assume that the other players will not see the sequence that won by the prior player?
      - Playing in the cli players might see the correct answer and cheat.
    - If at the end of the game there were players who didn't figure out the sequence should I just rank them last together?
  - What messages did I want the player to see on the screen as they played?

## Code Design
- When thinking about the design of the game in the code, I was really curious as to what I could potentially need.
- A file for 
  - constants,
  - cli,
  - the api (random.org api),
  - game logic,
  - potentially a formatting file? (Keep wording consistent and easy to tweak without hunting through logic files),
  - models (gameConfig, player, and potentially more)
  - guess tracker (Correct locations / correct numbers computed here for each attempt. will return it back to the game so it doesn't save anything here)
  - ReadMe doc of course

- I've also created a simple flow chart to map out all the possiblites in terms of how the game is played starting from when the user picks single player or multiplayer mode. Up until this point I've only mapped out how the whole game will be played and all the little details at each level so far.
- I've raised questions to myself to really understand how every component of the game will work at each possible point in the game. 
- Figuring out all the ambigous parts of the game and deciding how I want it to be played.
- One thing I did note is that I shouldn't keep trying to extend the game too much before coding. Although it's great to think of all the possibilites of what can be included in the game, I realized it will get far too complex before I even get a working product. I have more that I'd love to implement if time is on my side but for now this should be a great starting point to creating a unique mastermind game.


(8/21/2025)

## constants file
- I feel like starting with constants was the most important because these are components that won't change throughout the game
- Constants such as:
  - Game dialogue
  - Difficulty levels
  - Amount of numbers in the random sequence
  - Amount of attempts
  - Commands in the game (hint and guess history)
- After creating all the prompts I ran a quick loop to print out all messages so I can confirm it's formatted how I want it.

## score file
- This next file is going to host the code for calculating the locations and correct numbers
- It is to take the current guess and check:
  - First is the random sequence and guess the same length?
  - Iterate through the guess sequence and figure if the number at current index n are the same in both the guess sequence and random sequence
  - Figure out how many numbers are correct in the guess sequence
  - Should the calculation of the {guess sequence == random number sequence} be calculated here too?
    - For now I will just return the (correct location, correct numbers)
    - We know that if {correct locations == len(random number sequence)} than it's a match.
    - However {correct numbers != len(random number sequence)} is not a match
    - ^ very important distinction
  - Must handle duplicate numbers!
  - Dict vs Tuple for returning values?
      - I believe tuple is better for use because:
          - only using two integers to return
          - immutable
          - dict seems overkill for the impl
          - ex: correct_numbers, correct_locations = score_guess(secret, guess)
- Steps to be taken:
    - 1. check lengths
    - 2. calculate exact matchs (correct location)
    - 3. count freq of each number in both sequences (store in dict counter and create two counters)
    - 4. gather all the digits from each and combine into one unique set that host digits appearing in both sequences without duplicating (union?)
    - 5. loop through and add min(secret_count, guess_count) to final counter for "correct numbers"
    - 6. return correct numbers and correct locations

    **Example**
    - len() == len()
    - loop {
        loop through secret number see if secret[n] == guess[n]
    }
    - counter()
    - new = set1() | set2()
    - loop {
        counter += min(secret, guess)
    }
    - return (correct numbers, location)

## models file
- Creating this file to create the player(s) and game rules as well
- I know a need a game config object for:
    - length of the game
    - attempts
    - shared secret
    - num of players
- Definitely will need a player object:
    - their secret random number
    - attempts
    - hints
    - did they solve
    - history (guess + correct location, correct numbers)
    - current player number
- A way to track the players turn for multiplayer? 
- An object to tie the whole game togther
- Now I'm not sure if I need to add the score to the player class since each one is unique. 
    - Just realized it will be going in the history attribute
- 4 classes (player, game rules, current player, and and one to wrap them all together into a game)

## API for RandomAPI
- Created another project to test the api out first here's a solution that worked that i'll implement here:
- First I set up a virtual environment for the project:
    - Create a virtual environment (python3 -m venv venv)
    - Activate the virtual environment (source venv/bin/activate)
    - Install the required packages (pip install requests)
- Now the code:
```python 
def fetch_secret(length: int) -> list[int]:
    """Fetch random digits (0-7) from Random.org."""
    # https://www.random.org/integers/?num=4&min=0&max=7&col=1&base=10&format=plain&rnd=new
    
    url = f"{RANDOM_ORG_BASE}/integers/"
    params = {
        "num": length,
        "min": DIGIT_MIN,
        "max": DIGIT_MAX,
        "col": 1,
        "base": 10,
        "format": "plain",
        "rnd": "new",
    }
    headers = {"Accept": "text/plain", "User-Agent": "MastermindCLI/1.0"}

    def is_valid_sequence(digits: list[int]) -> bool:
        return len(digits) == length and all(0 <= d <= 7 for d in digits)

    def parse_response(text: str) -> list[int]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return [int(x) for x in lines]

    for attempt in range(RANDOM_ORG_MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, timeout=RANDOM_ORG_TIMEOUT_SEC, headers=headers)
            resp.raise_for_status()
            
            digits = parse_response(resp.text)
            if is_valid_sequence(digits):
                return digits
            
            raise ValueError("Invalid sequence from Random.org")
            
        except Exception:
            if attempt < len(RANDOM_ORG_RETRY_BACKOFFS):
                time.sleep(RANDOM_ORG_RETRY_BACKOFFS[attempt])
            continue
    
    raise SystemExit("Failed to fetch random numbers after retries")
 ```
- Added the code and the rng worked. 
- Created virtual env for project
- .gitignore for pycache and venv
- Requirements text for other users who pull from github
- Added more constants to use for the api class
- Made simple test for api to make sure it worked


(8/22/2025)

## formatting file
- This will be similar to the api and score files in which it'll be to help format things like:
    - hints
    - guess remaining
    - scoreboard
    - current location 
    - game dialogue for guess history
    - ***believe that is everything***
- Should be everything you see in the cli should be formatting here.
- Should not crowd the core game file and cli file with this code.
- Using it to separate the code to make it look cleaner
- Not sure if I'll be using this for the scoreboard and keep tracking of players.
    - thinking it'll be repetitve to create a function to keep track of players for the game because my models roundState function will be doing that
    - ^ if it works properly 
    - ***when building game logic make sure roundState is tracking properly before trying to implement it in formatting***
- Created test file to make sure the formatting looks how I want
- oops forgot to add in feedback after someone answers.
- Whilst creating the tests for this file I realized I haven't tested the score function to make sure it works properly

## game config
- Before I wanted to dive into the actual game logic, I wanted all the different components of the game created and each file has been test to make sure I'm getting the right response.
- For me, I'm thinking if I'm creating the game config whilst trying to create all the components, I would miss certain things that I needed.
- Thinking about what was needed for the game to even run before building the actual game was important to me
- I have:
    - the scoring logic for the location and correct numbers created
    - dialogue for the cli depending on which option the player enters (ex: types "#" for hint and I've created the dialogue for that)
    - player and game objects
    - created the api first in another project folder to test how the api works and to get a working function. imported it here after
    - a test file for each of these ^ to make sure they all work properly before working on the actually game logic
- I'm thinking that I needed to create these components individually before tackling this beast
- Now that I have all the things necessary to create the actual logic it should just be about connecting the pieces.
- Some questions:
    - Should I create the cli file first? This is where I'll run the game. The cli file will call the game file. At the same time the cli file can't really be created before the game file right?
    - It's like the game file is dependent on all the other files being created (models, formatting, etc) before I can piece it together. such as the cli file is dependent on the game?
- Also, what is needed in this game file?
    - **all the logic such as:**
        - 1. building the game
        - 2. checking if the player wants multiplayer or single player
        - 3. If multiplayer:
            - first: how many players? (1-4)
            - second: do they want a shared rng or a unique rng per player
        - 4. player(s) will choose difficulty
        - 5. player(s) get built
        - 6. game starts:
            - All games regardless of player count will have the options to choose hint, guess history, or enter a guess at beginning of each turn
            - If player choose hint, they will lose a guess. Although I'm not sure as of right now if I want them to skip a turn by getting a hint of just deducting a guess but still letting them play.
            - Choosing guess history should display their history (guess + feedback (location, correct nums)) followed by the game giving them the prompt again
            - single player:
                - keeps going until they either get the guess right or they use up all their guesses and lose
                - should display the secret rng if player didn't guess right
            - multiplayer:
                - players will keep playing until:
                    - all players guess the number
                    - players use up all their guesses
                - will display scoreboard at end of game with ranking depending on how many guesses they have left
                - should display the secret rng for players who didn't guess correctly
            - At the end of every game it will prompt if they want to play again or not
- Think I hit home on all the relevant and important details regarding game flow and how this file should look.
**Progress Update**
- so i created the game logic and hopefully hit all points i have listed out.
- I extensively tested each function and checked each players attributes to make sure it is tracking right such as:
    - history
    - feedback
    - attempts
    - guess
    - secret
    - made sure advance_turn is tracking the next player properly
    - scoreboard
    - game is getting built correctly
- I believe I hit all the main ideas of the game. will add anything necessary/forgotten once i build the cli file


(8/23/2025)

## CLI file
- Now just got to combine all the game logic together with the actual flow of the game in the cli
- basically have to write this again but for the cli and adding the dialogue from the constants file:
    - **all the logic such as:**
        - 1. building the game
        - 2. checking if the player wants multiplayer or single player
        - 3. If multiplayer:
            - first: how many players? (1-4)
            - second: do they want a shared rng or a unique rng per player
        - 4. player(s) will choose difficulty
        - 5. player(s) get built
        - 6. game starts:
            - All games regardless of player count will have the options to choose hint, guess history, or enter a guess at beginning of each turn
            - If player choose hint, they will lose a guess. Although I'm not sure as of right now if I want them to skip a turn by getting a hint of just deducting a guess but still letting them play.
            - Choosing guess history should display their history (guess + feedback (location, correct nums)) followed by the game giving them the prompt again
            - single player:
                - keeps going until they either get the guess right or they use up all their guesses and lose
                - should display the secret rng if player didn't guess right
            - multiplayer:
                - players will keep playing until:
                    - all players guess the number
                    - players use up all their guesses
                - will display scoreboard at end of game with ranking depending on how many guesses they have left
                - should display the secret rng for players who didn't guess correctly
            - At the end of every game it will prompt if they want to play again or not
- the cli should follow this exact flow of the game. we have all functions to perform these actions 

## Improvements/Additions
- I really want to expand on the current game I have and here's a few thoughts:
    - multiplayer server like among us?
        - would start up the server here and than share it to others
        - answers could be hidden if playing in shared mode and potentially won't even need the option for shared or unique secrets
        - could create voting system for players to choose if they want a shared or unique secret (if tie than game randomly picks)
        - share a code or server numbers
    - display number of attempts on leaderboard?
    - should i create a web interface? 
        - would mean the cli file would be irrelevant and I'd need to create a wnole new frontend file
    - power hints one per game: “reveal one correct position with correct number”
    - timed turns
    - daily challenge? if made into a server just like wordle
    - bots for single player? **i liked this idea**

## *Bot development (first addition to current game)*
- creating a bot to play against a solo player if he feels lonely or wants a challenge
- how the flow would look:
    - player chooses single mode
    - gets prompted something like:
        - solo
        - versus bot 
    - player picks bot
    - player now chooses match type:
        - shared rng
        - unique rng for both and player
    - player now chooses bot difficulty:
        - normal (casual, makes mistakes)
        - medium (smarter)
        - hard (expert, highly efficient solver)
    - player than chooses difficulty mode for game (4, 5, or 6 rng)
    - game starts...
- going to need to create 3 bots with varying difficulty
- ***shared foundation across all 3 bots***
    - bots only see what a human would: their own guesses and feedback (correct-place, correct-digit). Never peek at the secret
    - add a thinking delay range (1-5 seconds?) so it feels alive
    - standard alternating turns
    - winner will be chosen based on how many attempts they have left (because hints remove attempts)
    - if player and bot are on same turn and player guesses it right, the bot will have one turn to get it right
    - if tied at the end than you can choose to play again (prompts you back to very beginning where you choose single/multiplayer) or exit
    - bots will be able to use hints
    - bot difficulty designs:
        - info digestion: bot can use its past history and see your answers (shared rng only) to make its guess
        - if playing unique rng than bot will not look at your answers since it will not help
        - duplicates: fully respects duplicate digits (multiset logic)
        - no rule breaks: always the right length, valid digits (0-7), no exact duplicate guesses
        - “mistake rate” means intentional sub optimal choices that keep it fun for player (goes down the higher the bot difficulty)

- **refined foundation across bots**
    - match types:
        - shared code: you and the bot each try to crack the same secret
        - separate codes: you and the bot each try to crack your own secret
    - the bot does not see your guesses or feedback, and you do not see the bots
    - on the player UI during the game, the only bot status line is neutral “Bot made a guess.” (wont know how many attempts or hint its used)
    - full histories and outcomes are revealed only on the end scoreboard
    - standard alternating turns b/w player and bot
    - if one side solves early, they enter a dormant state and their later turns they auto pass silently (still shown as “Bot made a guess.”), while the other side continues until solved or out of attempts
    - game ends when both sides have either solved or exhausted attempts, then show the scoreboard
    - winner is based on how many attempts they have left. who ever has more attempts left wins (means took less turns to solve)
    - naturally penalizes hint usage ^^^
    - if attempts left are equal: rock/paper/scissors (best of 3)
    - scoreboard (what’s shown):
        - solved or not solved
        - history (guesses + feedback)
        - how many attempts a player/bot has left
        - winner banner saying (example: "Player won!"), if needed, RPS result (example: “Player won RPS 2–1”)
    - hints
        - each hint immediately deducts 1 attempt
        - max 1 hint per game per side and no hint before turn 3
        - if the bot uses a hint, show only: “Bot used a hint.” (Do not reveal hint content during play.)
        - use your game’s existing hint types (f"{digit} is in {ordinal(pos + 1)} position"). Content is applied only to the requesting side
        - usage based on different bot level: **as of writing this im not set on these rules but when building bots will probably refine**
            - normal:
                - from turns 4–7, if not solved: 35–50% chance each turn to use its single hint, regardless of progress
                - never uses a hint after turn 7
            - medium:
                - use 1 hint if no improvement for numbers in correct place for 3 consecutive turns and (current attempts left is < 5)
                - 6 digit games, allow this to trigger one turn earlier (from turn 4)
            - hard:
                - use hint anytime after these two requirements have been made:
                    - 2 attempts have been made
                    - 2 consecutive turns produced the same feedback pattern or internal estimate suggests finishing would likely exceed remaining attempts by > 1
    - thinking delay instead of instant response to make it more human (haven't figured out exact timing yet)
    - bots fully respect multiset logic and rely on the engine’s feedback function as source of truth (they will have no access to the secret sequence that was generated)
    - no rule breaks: always correct length, digits 0–7, and no exact duplicate guesses
    - mistake rate: selection only (choosing a lower information but legal guess), decreasing with difficulty:
        - normal: noticeable 15-25 % of turns pick a lower info guess. feels human? (honestly not sure what the percent should be)
        - medium: minimal 10-15% of turns pick a lower info guess
        - hard: none (or negligible) 5-10% of turns pick a lower info guess (near optimal guesses)
        - no backtracking: never choose a guess inconsistent with prior feedback
        - after a hint: next turn has 0% mistake chance (meaning atleast 1 number in the guess should be correct)
        - could either code a percentage or a top-K sampling
    - visibility & messaging rules:
        - show player feedback only to the player
        - for the bot: prompt “Bot is thinking…” during the delay → and when they made a guess show this prompt “Bot made a guess.”
        - after game: reveal full histories, outcomes, and metrics on the scoreboard for bot **only**

- **revising this slightly**
- removing:
    - difficulty levels for bot is getting removed as researching how to create different guessing strategies is becoming far too complex and dont know if I'd even be able to implement them all on time
    - plus even brainstorming and figuring out what type of guessing strategy to implement has been challenging
- trying to keep the bot between normal - medium level difficulty as a standard
- researching and trying to figure out the best way to implement a bot where the guess strategy isn't too complex but still poses a challenge to the player
- here's the strategies i've come across on google and talking with gpt:
    - Opening Script: play two fixed “spread” guesses to quickly learn which digits are present.
    - Random-from-Candidates (RFC): after pruning, take the first unseen candidate from a (once) shuffled bag.
    - First-Consistent (FC): pre-shuffle the universe/pool once; each turn pick the earliest code still consistent.
    - Frequency-Best (Greedy): for each position, choose the most common digit among remaining candidates; nudge if you’d repeat.
    - Bucket-Pick (Rules): classify candidates as Good/OK/Bad by simple rules (uniqueness, repeats) and pick randomly from the best bin.
    - Beam-Width-1: scan a small pool with a simple score and keep only the single best seen (no sorting).
    - Two-Dice (Tournament): sample two random candidates, score both, pick the better—adds bias without sorting.
    - Position-Sweep (Lock-In): freeze positions that look right; cycle likely digits through the remaining slots.
    - Top-K Sampling: rank candidates, keep the top K, and pick randomly among them for human-like variety.
    - Info-Gain / Best-Split: choose the guess that minimizes the largest feedback bucket (worst-case survivors) using sampled evaluation.
    - Endgame Clamp: when few candidates remain (≈8–12), stop heuristics and guess directly from the remaining bag.
    - articles:
        - https://stackoverflow.com/questions/62430071/donald-knuth-algorithm-mastermind
        - https://supermastermind.github.io/playonline/optimal_strategy.html
- i'm not even sure in terms of efficiency how good or bad most of them even are at this moment/
- maybe i'll have a mixture two of them or even put my own twist on one of the strategies i've come across
- im still not sure which strategy i want to pick but i do know i want all the technical details about the bot figured out and written out before i start building.
- having the flow in the cli, dialogue, rules, and bot difficulty level confirmed is important to me so i have a foundation
- sure ill maybe twink the rules a bit as i go but having the difficulty figureed out before i begin because that's the most complex part of the whole bot

##other notes for bot
- will the player experience be better or worse if i show the the bots guess? or will it keep it fun by the player not knowing what the bot is doing
- should the bots actions be shown in the cli?
- im starting to feel like it'll make the player experience better to know that they are actually playing against a bot when they see the actions in the cli instead of just "bot is thinking" and "bot made a guess your turn"
- will ask others for feedback so i can make the experience for the player as fun as possible


(8/22/2025)

        
##backend additions
- whilst working on break started brainstorming more ways to secure my backend and from my time at atlassian i remember having to implement all these
- going to implement a simple rate limiter, logging, and possibly circuit breaker for the api.
- https://martinfowler.com/bliki/CircuitBreaker.html
- https://pypi.org/project/circuitbreaker/
- https://stackoverflow.com/questions/40748687/python-api-rate-limiting-how-to-limit-api-calls-globally
- logging:
    - https://docs.python.org/3/library/logging.html
    - https://stackoverflow.com/questions/16337511/log-all-requests-from-the-python-requests-module
- files to be changed/added (just from top of my head):
    - random_org (api file needs to obv implement these)
    - new files to separate it from the api file (so it keeps everything clean and easy to read):
        - logging file? not sure as of right now if i need a whole new file or if i can just implement it into the current code without having to create whole new file
        - circuit breaker (open, close, half open)
        - rate limiting 
- https://pypi.org/project/circuitbreaker/
- Tried doing a fastapi REST impl currently not working tho. was researching how to implement REST api 








        


