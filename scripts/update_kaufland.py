import requests
import json
from datetime import datetime

URL = "https://silent-resonance-db8bpromo-proxy.kaloqnpanchev.workers.dev/kaufland"


headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "Accept": "application/json",
    "Referer": "https://www.kaufland.bg/"
}

params = {
    "query": "",
    "sort": "discount",
    "page": 1,
    "size": 200
}

resp = requests.get(URL, headers=headers, params=params, timeout=30)

if resp.status_code != 200:
    raise Exception(f"Kaufland API error: {resp.status_code}")

# ако не е JSON, спираме с ясен error
if not resp.text.strip().startswith("{"):
    raise Exception("Kaufland did not return JSON (HTML protection page)")

data = resp.json()

products = data.get("products", [])

crazy = []
big = []
categories = {
    "fruits_vegetables": [],
    "dairy": [],
    "meat": []
}

for p in products:
    old = p.get("oldPrice")
    new = p.get("price")

    if not old or not new:
        continue

    discount = int((old - new) / old * 100)

    item = {
        "id": p.get("id"),
        "name": p.get("name"),
        "price": new,
        "oldPrice": old,
        "discount": discount,
        "image": p.get("image"),
        "validTo": p.get("validTo")
    }

    if new <= 0.19:
        crazy.append(item)
    elif discount >= 40:
        big.append(item)

    cat = (p.get("category") or "").lower()
    if "плод" in cat or "зелен" in cat:
        categories["fruits_vegetables"].append(item)
    elif "мля" in cat or "сир" in cat:
        categories["dairy"].append(item)
    elif "мес" in cat or "пил" in cat:
        categories["meat"].append(item)

result = {
    "updatedAt": datetime.utcnow().isoformat(),
    "store": "Kaufland",
    "currency": "EUR",
    "highlighted": {
        "crazyDeals": crazy,
        "bigDiscounts": big
    },
    "categories": categories
}

with open("kaufland.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
