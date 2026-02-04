import subprocess
import time
import requests
import pytest

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def flask_server():
    proc = subprocess.Popen(
        ["python", "app/run_flask_for_tasks.py"], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    for _ in range(5):
        try:
            requests.get("http://127.0.0.1:5000")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        proc.terminate()
        raise RuntimeError("Flask server failed to start")

    yield

    proc.terminate()
    proc.wait()

def test_user_journey():
    r = requests.post(
        f"{BASE_URL}/add",
        json={"item": "e2e_item", "amount": 10}
    )
    assert r.status_code == 200

    r = requests.post(
        f"{BASE_URL}/remove",
        json={"item": "e2e_item", "amount": 4}
    )
    assert r.status_code == 200

    r = requests.get(f"{BASE_URL}/inventory")
    data = r.json()

    item = next(i for i in data if i["item_name"] == "e2e_item")
    assert item["amount"] == 6
