from typing import Optional
from threading import RLock
from models import GameState

_lock = RLock()
_current: Optional[GameState] = None

def set_current(state: GameState) -> None:
    with _lock:
        global _current
        _current = state

def get_current() -> Optional[GameState]:
    with _lock:
        return _current
