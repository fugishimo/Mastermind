from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from bridge import get_current

app = FastAPI(title="mastermind-live", version="1.0.0")

# class PlayerState(BaseModel):
#     index: int
#     attempts_left: int
#     solved: bool
#     hints_used: int
#     history: List[str]

# class LiveStateResp(BaseModel):
#     finished: bool
#     length: int
#     attempts: int
#     num_players: int
#     shared_secret: bool
#     current_player_index: int
#     players: List[PlayerState]

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


# @app.get("/live/state", response_model=LiveStateResp)
# def live_state():
#     g = get_current()
#     if not g:
#         raise HTTPException(404, "no_active_game")
#     players = [
#         PlayerState(
#             index=p.index,
#             attempts_left=p.attempts_left,
#             solved=p.solved,
#             hints_used=p.hints_used,
#             history=p.history,
#         )
#         for p in g.players
#     ]
#     return LiveStateResp(
#         finished=g.finished,
#         length=g.config.length,
#         attempts=g.config.attempts,
#         num_players=g.config.num_players,
#         shared_secret=g.config.shared_secret,
#         current_player_index=g.round_state.current_player_idx + 1,
#         players=players,
#     )

@app.get("/live/secrets",response_model=Secrets)
def get_secrets():
    g = get_current()
    if not g:
        raise HTTPException(404, "no_active_game")
    current_player = g.players[g.round_state.current_player_idx]
    return Secrets(current_player_secret=current_player.secret)

# @app.get("/live/scoreboard", response_model=LiveScoreboardResp)
# def live_scoreboard():
#     from game import build_scoreboard
#     g = get_current()
#     if not g:
#         raise HTTPException(404, "no_active_game")
#     ranked = build_scoreboard(g.players)
#     entries = [ScoreboardEntry(rank=rank, player_index=p.index, solved=p.solved, attempts_taken=p.attempts_taken_to_solve if p.solved else None) for rank, p in ranked]
#     return LiveScoreboardResp(finished=g.finished, scoreboard=entries)
@app.get("/live/scoreboard", response_model=LiveScoreboardResp)
def live_scoreboard():
    from game import build_scoreboard

    g = get_current()
    if not g:
        raise HTTPException(404, "no_active_game")

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
        raise HTTPException(404, "no_active_game")
    
    current_player = g.players[g.round_state.current_player_idx]
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
