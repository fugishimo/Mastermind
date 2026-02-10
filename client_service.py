# client_service.py
import requests
from typing import Optional, List, Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def create_game(mode: str, difficulty: str, num_players: int = 1, shared_choice: Optional[str] = None) -> Dict[str, Any]:
    payload = {
        "mode": mode,
        "difficulty": difficulty,
        "num_players": num_players,
        "shared_choice": shared_choice
    }
    r = requests.post(f"{BASE_URL}/games", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def get_game(game_id: str) -> Dict[str, Any]:
    r = requests.get(f"{BASE_URL}/games/{game_id}", timeout=10)
    r.raise_for_status()
    return r.json()

def submit_guess(game_id: str, guess: List[int]) -> Dict[str, Any]:
    r = requests.post(f"{BASE_URL}/games/{game_id}/guess", json={"guess": guess}, timeout=10)
    r.raise_for_status()
    return r.json()

def take_hint(game_id: str) -> Dict[str, Any]:
    r = requests.post(f"{BASE_URL}/games/{game_id}/hint", timeout=10)
    r.raise_for_status()
    return r.json()
