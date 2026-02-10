from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from bridge import get_current
import logging
from random_org import fetch_secret

app = FastAPI(title="mastermind-live", version="1.0.0")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

class Mastermind(BaseModel):
    message: str

class ScoreboardEntry(BaseModel):
    rank: int
    player_index: int
    solved: bool
    attempts_left: int 

class LiveScoreboardResp(BaseModel):
    finished: bool
    scoreboard: List[ScoreboardEntry]

class Summary(BaseModel):
    finished: bool
    length: int
    num_players: int
    shared_secret: bool
    current_player_index: int
    current_player_attempts_left: int
    current_player_solved: bool
    current_player_hints_used: int
    current_player_history: List[str]   

class Secrets(BaseModel):
    current_player_secret: List[int]



@app.get("/", response_model=Mastermind)
def root():
    return {"message": "Welcome to the Mastermind. go to \"lhttp://127.0.0.1:8000/docs#\" to see the api working! hehe"}

@app.get("/live/secrets",response_model=Secrets)
def get_secrets():
    g = get_current()
    if not g:
        logging.warning("live_state: no_active_game")
        raise HTTPException(404, "no_active_game")
    current_player = g.players[g.round_state.current_player_idx]
    return Secrets(current_player_secret=current_player.secret)

@app.get("/live/scoreboard", response_model=LiveScoreboardResp)
def live_scoreboard():
    from game import build_scoreboard

    g = get_current()
    if not g:
        logging.warning("live_state: no_active_game")
        raise HTTPException(404, "no_active_game")
    
    logging.info("live state: active game: game_id active finished=%s", g.finished)

    ranked = build_scoreboard(g.players)

    entries: list[ScoreboardEntry] = []
    for rank, p in ranked:
        entry = ScoreboardEntry(
            rank=rank,
            player_index=p.index,
            solved=p.solved,
            attempts_left=p.attempts_left,
        )
        entries.append(entry)

    return LiveScoreboardResp(
        finished=g.finished,
        scoreboard=entries,
    )

@app.get("/live/summaryCurrentPlayer", response_model=Summary)
def summary():
    g = get_current()
    if not g:
        logging.warning("live_state: no_active_game")
        raise HTTPException(404, "no_active_game")
    
    current_player = g.players[g.round_state.current_player_idx]
    logging.info("live_state: current player index=%s and number of guesses left=%s", g.round_state.current_player_idx, current_player.attempts_left)
    return Summary(
        finished=g.finished,
        length=g.config.length,
        num_players=g.config.num_players,
        shared_secret=g.config.shared_secret,
        current_player_index=g.round_state.current_player_idx + 1,
        current_player_attempts_left=current_player.attempts_left,
        current_player_solved=current_player.solved,
        current_player_hints_used=current_player.hints_used,
        current_player_history=current_player.history,
    )

@app.post("/random/sequence")
def random_sequence(length: int = 4):
    try:
        digits = fetch_secret(length)
        return {"length": length, "sequence": digits}
    except SystemExit:
        logging.error("random_sequence: random.org failed")
        raise HTTPException(status_code=500, detail="random.org unavailable")
