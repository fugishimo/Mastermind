import threading
import asyncio
import uvicorn
# starts fastapi in a background thread so you dont have to
def _run_api():
    config = uvicorn.Config("api:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
    server = uvicorn.Server(config)
    # run the server in this thread’s event loop
    asyncio.run(server.serve())

def start_api_in_thread():
    t = threading.Thread(target=_run_api, name="api-thread", daemon=True)
    t.start()
    return t

# publish each new GameState created by game.init_game
def install_init_game_bridge():
    import game
    from bridge import set_current

    _orig_init = game.init_game

    def _wrapped_init(cfg):
        state = _orig_init(cfg)
        set_current(state)
        return state

    game.init_game = _wrapped_init 

def main():
    # start the API
    start_api_in_thread()
    # install the bridge so new games are visible in the API
    install_init_game_bridge()
    # run cli. didn't want to change this file plus couldn't get it work with new fastapi REST impl before
    import cli
    cli.main()

if __name__ == "__main__":
    main()
