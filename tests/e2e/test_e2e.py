import subprocess
import time
import requests
import pytest

@pytest.fixture(scope="session", autouse=True)
def start_flask():
    proc = subprocess.Popen(["python", "app.py"])
    time.sleep(5)  # wait for server
    yield
    proc.terminate()

BASE_URL = "http://localhost:5000"

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
