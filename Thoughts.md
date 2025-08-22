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
- Created another project to test the api out first here's a solution that worked:
- First I had to set up a virtual environment for the project:
    - Create a virtual environment (python3 -m venv venv)
    - Activate the virtual environment (source venv/bin/activate)
    - Install the required packages (pip install requests pytest)
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
        

        


