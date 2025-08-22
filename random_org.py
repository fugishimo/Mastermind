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
                return digits
            
            raise ValueError("Invalid sequence from Random.org")
            
        except Exception:
            if attempt < len(RANDOM_ORG_RETRY_BACKOFFS):
                time.sleep(RANDOM_ORG_RETRY_BACKOFFS[attempt])
            continue
    
    raise SystemExit("Failed to fetch random numbers after retries")