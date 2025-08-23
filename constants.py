# Difficulty Map
DIFFICULTY_MAP = {
  "1": 4,
  "2": 6,
  "3": 8
}

# Game Commands
HISTORY = "#"
HINT = "?"

# Random.org API
RANDOM_ORG_BASE = "https://www.random.org"
RANDOM_ORG_TIMEOUT_SEC = 5 # seconds    
RANDOM_ORG_MAX_RETRIES = 3 # number of retries
RANDOM_ORG_RETRY_BACKOFFS = [0.25, 0.5, 1.0] # seconds

# Limits for the game (max attempts, min and max digits for the random sequence)
MAX_ATTEMPTS = 10
MIN_DIGITS = 0
MAX_DIGITS = 7

# Game Messages
MSG_WELCOME = "Welcome to the Mastermind Game!\n"
MSG_MODE_PROMPT = "Type 1 for single player\nType 2 for multiplayer\n"
MSG_PLAYER_COUNT = "Type number for the amount of people playing than click enter (4 people max)\n"
MSG_SHARED_PROMPT = "Do you want all the players to have the same number combination? Type 1 for yes or 2 for no\n"
MSG_DIFFICULTY = (
    "Choose difficulty:\n"
    "Type 1 for normal (4 numbers)\n"
    "Type 2 for medium (6 numbers)\n"
    "Type 3 for hard (8 numbers)\n"
)

MSG_TURN_PROMPT = (
    'Type "#" for history of guesses and feedback,\n'
    'Type "?" for hints,\n'
    'Type your guess with a space in between each number then click enter (pick a number between 0 and 7)\n'
)
MSG_INVALID_INPUT = "Invalid input choose again.\n"
MSG_ONE_LEFT_NO_HINT = "You only have 1 guess remaining, you cannot ask for a hint. Please enter your guess.\n"
MSG_NO_HINTS_LEFT = "No hints remaining.\n"

MSG_ALL_CORRECT = "All correct! You win!\n"
MSG_OUT_OF_GUESSES = "Out of guesses! The correct sequence was: {secret}\n"

MSG_PLAY_AGAIN = "Do you want to play again? Type 1 for yes, 2 for no\n"

# Test loop for messages
# if __name__ == "__main__":
#     message_vars = {k: v for k, v in globals().items() if k.startswith('MSG_')}
#     for var_name, value in message_vars.items():
#         print(f"\n--- {var_name} ---")
#         print(value)
