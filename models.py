from dataclasses import dataclass, field
from typing import List, Optional, Set

# Game Config
@dataclass
class GameConfig:
    length: int                 # 4, 6, 8
    attempts: int               # always 10
    shared_secret: bool         # multiplayer: shared vs different secrets
    num_players: int            # 1-4 max
    duplicates_allowed: bool = True  # always True per spec

# Player
@dataclass
class Player:
    index: int                        # 1 based for display not 0 based
    secret: List[int]                 # player's secret (shared or individual)
    attempts_left: int                # starts at MAX_ATTEMPTS
    history: List[str] = field(default_factory=list)  # rendered history
    hints_used: int = 0               # caps: single=len(secret), multi=3
    hinted_positions: Set[int] = field(default_factory=set)  # unique positions hinted
    solved: bool = False
    attempts_taken_to_solve: Optional[int] = None     # personal guesses taken to solve

# Round State
@dataclass
class RoundState:
    current_player_idx: int = 0      
    # zero based index into players, will point to the current player,
    # will hopefully be used to track the current player's turn

# Game State
@dataclass
class GameState:
    config: GameConfig
    players: List[Player]
    round_state: RoundState
    finished: bool = False

