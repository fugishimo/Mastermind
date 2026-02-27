import time
import logging
import requests

from ratelimit import limits
from ratelimit.exception import RateLimitException
from circuitbreaker import circuit

from constants import (
    RANDOM_ORG_BASE,
    RANDOM_ORG_TIMEOUT_SEC,
    RANDOM_ORG_MAX_RETRIES,
    MIN_DIGITS,
    MAX_DIGITS,
)

logger = logging.getLogger(__name__)

FIFTEEN_MINUTES = 900  # 15 * 60


class RandomOrgError(Exception):
    """Random.org call failed after retries, returned invalid data, or hit rate limit."""


def _backoff(attempt: int) -> float:
    # simple exponential backoff: 0.5, 1, 2, 4... capped
    return min(0.5 * (2 ** attempt), 5.0)


def _fetch_once(length: int) -> list[int]:
    url = f"{RANDOM_ORG_BASE.rstrip('/')}/integers/"
    params = {
        "num": length,
        "min": MIN_DIGITS,
        "max": MAX_DIGITS,
        "col": 1,
        "base": 10,
        "format": "plain",
        "rnd": "new",
    }

    r = requests.get(url, params=params, timeout=RANDOM_ORG_TIMEOUT_SEC)
    r.raise_for_status()

    digits = [int(x) for x in r.text.split()]

    if len(digits) != length:
        raise RandomOrgError(f"Expected {length} digits, got {len(digits)}")
    if not all(MIN_DIGITS <= d <= MAX_DIGITS for d in digits):
        raise RandomOrgError("Digit out of allowed range")

    return digits


@circuit(
    failure_threshold=5,
    recovery_timeout=30,
    expected_exception=(Exception,),
    name="random_org",
)
@limits(calls=10, period=FIFTEEN_MINUTES)
def fetch_secret(length: int) -> list[int]:
    """
    - Rate limited: 10 calls / 15 minutes (FAIL FAST, no sleeping)
    - Circuit breaker: opens after 5 failed operations
    - Resiliency: retries with exponential backoff (network + parsing issues)
    """
    try:
        last_err: Exception | None = None

        for attempt in range(RANDOM_ORG_MAX_RETRIES):
            try:
                return _fetch_once(length)

            except (requests.RequestException, ValueError, RandomOrgError) as e:
                last_err = e
                if attempt < RANDOM_ORG_MAX_RETRIES - 1:
                    time.sleep(_backoff(attempt))
                continue

        logger.exception("Random.org failed after retries", exc_info=last_err)
        raise RandomOrgError("Random.org failed after retries") from last_err

    except RateLimitException as e:
        # fail fast instead of sleeping for potentially minutes
        raise RandomOrgError("Rate limit exceeded (10 calls / 15 minutes). Try again later.") from e