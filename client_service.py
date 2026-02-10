import requests

BASE_URL = "http://127.0.0.1:8000"

#using http client to call our own FastAPI endpoint to get a random sequence. instead of client calling from the cli.
#now using player to call http client - server endpoint - calls api to retrieve sequence
def get_random_sequence(length: int) -> list[int]:
    resp = requests.get(f"{BASE_URL}/random/sequence", params={"length": length}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["sequence"]
