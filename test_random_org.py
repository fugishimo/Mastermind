# scripts/test_random_org.py
from random_org import fetch_secret

def main():
    numbers = fetch_secret(4)  # fetch 4 random digits
    print("Random sequence:", " ".join(map(str, numbers)))

if __name__ == "__main__":
    main()