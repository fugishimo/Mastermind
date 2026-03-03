# api.py
from secrets import token_hex

from fastapi import FastAPI, HTTPException, Header
from typing import Dict
from uuid import uuid4
import logging
from models_api import (
    CreateGameRequest,
    CreateGameResponse,
    PlayerPublic,
    GamePublicState,
    GuessRequest,
    GuessResponse,
    HintResponse,
)

import game  # server-side domain logic
from models import GameState

app = FastAPI(title="mastermind-live", version="2.0.0")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# In-memory game store (server-owned)
GAMES: Dict[str, GameState] = {}

# ---------- Helpers ----------
def _get_game(game_id: str) -> GameState:
    g = GAMES.get(game_id)
    if not g:
        raise HTTPException(404, "game_not_found")
    return g

def _public_state(game_id: str, g: GameState) -> GamePublicState:
    players = []
    for p in g.players:
        players.append(PlayerPublic(
            index=p.index,
            attempts_left=p.attempts_left,
            solved=p.solved,
            hints_used=p.hints_used,
            history=p.history,
        ))
    return GamePublicState(
        game_id=game_id,
        finished=g.finished,
        length=g.config.length,
        attempts=g.config.attempts,
        num_players=g.config.num_players,
        shared_secret=g.config.shared_secret,
        current_player_index=g.round_state.current_player_idx + 1,
        players=players,
    )

# ---------- Endpoints ----------
@app.post("/games", response_model=CreateGameResponse, status_code=201)
def create_game(req: CreateGameRequest):
    cfg = game.build_game_config(req.mode, req.num_players, req.shared_choice, req.difficulty)
    state = game.init_game(cfg)  # server generates secret(s) inside create_players()
    state.token = token_hex(32)
    game_id = str(uuid4())
    GAMES[game_id] = state
    logging.info("games:create id=%s players=%d shared=%s length=%d",
                 game_id, cfg.num_players, cfg.shared_secret, cfg.length)
    return CreateGameResponse(
        game_id=game_id,
        token=state.token,
        length=cfg.length,
        attempts=cfg.attempts,
        num_players=cfg.num_players,
        shared_secret=cfg.shared_secret
    )

@app.get("/games/{game_id}", response_model=GamePublicState)
def get_game(game_id: str):
    g = _get_game(game_id)
    return _public_state(game_id, g)

@app.post("/games/{game_id}/hint", response_model=HintResponse)
def take_hint(game_id: str, token: str = Header(...)):
    g = _get_game(game_id)
    _verify_token(g, token)
    p = game.current_player(g)

    if p.attempts_left <= 1:
        raise HTTPException(400, "one_left_no_hint")
    if not game.can_take_hint(p, g.config):
        raise HTTPException(400, "no_hints_left")

    hint_text = game.give_hint(p, g.config)

    # if nobody can play after spending hint attempt, finish
    if not game.any_player_can_play(g):
        g.finished = True

    return HintResponse(hint=hint_text, attempts_left=p.attempts_left)

@app.post("/games/{game_id}/guess", response_model=GuessResponse)
def submit_guess(game_id: str, req: GuessRequest, token: str = Header(...)):
    g = _get_game(game_id)
    _verify_token(g, token)
    if g.finished:
        raise HTTPException(400, "game_finished")

    p = game.current_player(g)
    if p.solved or p.attempts_left == 0:
        # skip player automatically
        game.advance_turn(g)
        p = game.current_player(g)

    # Validate guess length
    if len(req.guess) != g.config.length:
        raise HTTPException(400, "invalid_guess_length")

    correct_numbers, correct_locations, feedback = game.process_guess(p, req.guess)

    # advance or finish
    if not game.any_player_can_play(g):
        g.finished = True
    else:
        game.advance_turn(g)

    return GuessResponse(
        feedback=feedback,
        correct_numbers=correct_numbers,
        correct_locations=correct_locations,
        solved=p.solved,
        attempts_left=p.attempts_left,
        finished=g.finished,
    )

# ---------- Helper ----------
def _verify_token(g: GameState, token: str):
    if token != g.token:
        raise HTTPException(403, "invalid_token")
