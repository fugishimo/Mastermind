from score import score_guess

def main():
    print("=== score_guess tests ===")
    print("\n")
    # 1. No matches
    secret = [1, 2, 3, 4]
    guess = [5, 6, 7, 8]
    print(secret, guess, "->", score_guess(secret, guess))  # (0, 0)
    print("\n")
    # 2. One exact match
    secret = [1, 2, 3, 4]
    guess = [1, 5, 6, 7]
    print(secret, guess, "->", score_guess(secret, guess))  # (1, 1)
    print("\n")
    # 3. Some numbers correct, mixed positions
    secret = [1, 2, 3, 4]
    guess = [4, 3, 2, 1]
    print(secret, guess, "->", score_guess(secret, guess))  # (4, 0)
    print("\n")
    # 4. Duplicates in secret
    secret = [1, 1, 2, 3]
    guess = [1, 2, 1, 1]
    print(secret, guess, "->", score_guess(secret, guess))  # (3, 1)
    print("\n")
    # 5. All exact matches
    secret = [7, 7, 7, 7]
    guess = [7, 7, 7, 7]
    print(secret, guess, "->", score_guess(secret, guess))  # (4, 4)
    print("\n")
    # 6. Length mismatch (should raise ValueError) Although I'm not sure if this is needed because we should be checking before we get to this
    try:
        secret = [1, 2, 3]
        guess = [1, 2]
        print(secret, guess, "->", score_guess(secret, guess))
    except ValueError as e:
        print("Length mismatch:", e)


if __name__ == "__main__":
    main()
