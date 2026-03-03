from pydantic import BaseModel, Field
from typing import List, Optional

# ---------- Models ----------
class CreateGameRequest(BaseModel):
    mode: str = Field(..., description='1 single, 2 multi')
    difficulty: str = Field(..., description='1=4,2=6,3=8')
    num_players: Optional[int] = Field(1, ge=1, le=4)
    shared_choice: Optional[str] = Field(None, description='multi only: 1 shared, 2 different')

class CreateGameResponse(BaseModel):
    game_id: str
    token: str
    length: int
    attempts: int
    num_players: int
    shared_secret: bool

class PlayerPublic(BaseModel):
    index: int
    attempts_left: int
    solved: bool
    hints_used: int
    history: List[str]

class GamePublicState(BaseModel):
    game_id: str
    finished: bool
    length: int
    attempts: int
    num_players: int
    shared_secret: bool
    current_player_index: int
    players: List[PlayerPublic]

class GuessRequest(BaseModel):
    guess: List[int]

class GuessResponse(BaseModel):
    feedback: str
    correct_numbers: int
    correct_locations: int
    solved: bool
    attempts_left: int
    finished: bool

class HintResponse(BaseModel):
    hint: str
    attempts_left: int