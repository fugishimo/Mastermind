import requests
import time
from constants import (
    MIN_DIGITS,
    MAX_DIGITS,
    RANDOM_ORG_BASE,
    RANDOM_ORG_TIMEOUT_SEC,
    RANDOM_ORG_MAX_RETRIES,
    RANDOM_ORG_RETRY_BACKOFFS,
    )
import logging   
from ratelimit import limits, sleep_and_retry
from circuitbreaker import circuit

FIFTEEN_MINUTES = 600 #used 10 seconds to test the  rate limiter 600 is for the actual program

#basically have 15 total attempts to call api before we trip the circuit breaker. 
#if we fail to fetch the secret 3 times (retry limit = 3) than that will be 1 of 5 attempts, leaving 4 left to trip it
@circuit(
    failure_threshold=5,              # 5 full fetch_secret failures in a row (15 attempts total to call api)
    recovery_timeout=30,              # after 30s, half open allows a test call
    expected_exception=(
        requests.exceptions.RequestException,  # network/HTTP errors
        ValueError,                            # invalid sequence
        SystemExit,                            # your final "gave up after retries" (technically this is the only one that really matters)
    ),
    name="random_org_fetch"
)
@sleep_and_retry
@limits(calls=10, period=FIFTEEN_MINUTES)
def fetch_secret(length: int) -> list[int]:
    """Fetch random digits (0-7) from Random.org."""
    # https://www.random.org/integers/?num=4&min=0&max=7&col=1&base=10&format=plain&rnd=new
    
    url = f"{RANDOM_ORG_BASE}/integers/"
    params = {
        "num": length,
        "min": MIN_DIGITS,
        "max": MAX_DIGITS,
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
                logging.info("valid sequence: length=%d attempts=%d taken to grab sequence", length, attempt)
                return digits
            
            logging.warning("Random.org grabbed an invalid sequence digits=%d", digits)
            raise ValueError("Invalid sequence from Random.org")
            
        except Exception:
            logging.warning("Trying again to fetch secret attempted=%d", attempt + 1)
            if attempt < len(RANDOM_ORG_RETRY_BACKOFFS):
                time.sleep(RANDOM_ORG_RETRY_BACKOFFS[attempt])
            continue

    logging.warning("Failed to fetch a valid sequence after retries length=%d and retries=%d", length, RANDOM_ORG_MAX_RETRIES)
    raise SystemExit("Failed to fetch random numbers after retries")