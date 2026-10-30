"""Check Next's stock for the navy petite Friends Like These dress in EU 34 and push a phone alert via ntfy."""

import json
import os
import sys
import urllib.request
from pathlib import Path

ITEM = "g99085"  # Navy Petite Chiffon Cape Satin Midi Dress
SIZE = "04"  # EU 34 / UK 6
STORES = {
    "CH": "https://www.nextdirect.com/ch/en/style/sv034337/g99085",
    "DE": "https://www.next.de/en/style/sv034337/g99085",
}
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
STATE_FILE = Path(__file__).with_name("state.json")  # Last seen availability per store


def size_status(territory):
    url = f"https://api.nextdirect.com/api/stock/next/{territory}/en/v1/items/{ITEM}/options"
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=20) as resp:
        options = json.load(resp)["options"]
    return next(o["status"] for o in options if o["number"] == SIZE)


def notify(topic, territory, status):
    if status == "SoldOut":
        message = f"Navy EU 34 is sold out again at Next {territory}."
        headers = {"Title": "Kleid ist sold out", "Priority": "default", "Tags": "dress,x"}
    else:
        message = f"Navy EU 34 is {status} at Next {territory}. Buy now!"
        headers = {"Title": "Kleid ist in stock!", "Priority": "urgent", "Tags": "dress,rotating_light"}
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=message.encode(),
        headers={**headers, "Click": STORES[territory]},
    )
    urllib.request.urlopen(req, timeout=20)


def main():
    topic = os.environ.get("NTFY_TOPIC")
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    for territory in STORES:
        status = size_status(territory)
        print(f"{territory}: EU 34 -> {status}")
        available = status != "SoldOut"
        if available != state.get(territory, False):
            if topic:
                notify(topic, territory, status)
            state[territory] = available
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    sys.exit(main())
