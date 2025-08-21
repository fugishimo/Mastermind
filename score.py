from collections import Counter
from typing import List, Tuple

def score_guess(secret: List[int], guess: List[int]) -> Tuple[int, int]:

    # Calculate the score for a guess against the secret sequence.
    # Returns: tuple: (correct_numbers, correct_locations)

    # Check if guess and secret sequences are same length
    if len(guess) != len(secret):
        raise ValueError("Guess and secret sequences must be the same length")
    
    # Calculate exact matches (correct position and correct number)
    correct_locations = 0
    for position in range(len(secret)):
        if secret[position] == guess[position]:
            correct_locations += 1
    
    # Calculate total matches including duplicates
    secret_counter = Counter(secret)
    guess_counter = Counter(guess)
    
    # Get all unique digits that appear in either secret or guess
    all_digits = set(secret_counter) | set(guess_counter)
    
    # For each digit, count how many times it appears in both sequences and take the smaller of the two counts
    correct_numbers = 0
    for digit in all_digits:
        secret_count = secret_counter[digit]
        guess_count = guess_counter[digit]
        correct_numbers += min(secret_count, guess_count)
    
    return (correct_numbers, correct_locations)
