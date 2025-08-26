import time
import logging
from random_org import fetch_secret

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def main():
    print("Starting rate limit test...")
    start = time.time()

    #calling api more than 10 times which is the max to test
    for i in range(12):
        print(f"\nCall #{i+1}")
        try:
            result = fetch_secret(4)
            print(f"Fetched secret #{i+1}: {result}")
        except Exception as e:
            print(f"Error on call #{i+1}: {e}")

    elapsed = time.time() - start
    print(f"\nTest finished in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
