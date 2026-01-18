import requests
import json
from datetime import datetime

URL = "https://www.kaufland.bg/.rest/promotions"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "Accept": "application/json"
}

resp = requests.get(URL, headers=headers, timeout=30)

# ако не е 200 – спираме
if resp.status_code != 200:
    raise Exception(f"Kaufland API error: {resp.status_code}")

data = resp.json()

products = []

for p in data.get("items", []):
    old = p.get("oldPrice")
    new = p.get("price")
    if not old or not new:
        continue

    discount = int((old - new) / old * 100)

    if new <= 0.19 or discount >= 40:
        products.append({
            "id": p["id"],
            "name": p["name"],
            "price": new,
            "oldPrice": old,
            "discount": discount,
            "image": p.get("image"),
            "validTo": p.get("validTo")
        })

result = {
    "updatedAt": datetime.utcnow().isoformat(),
    "store": "Kaufland",
    "currency": "EUR",
    "highlighted": {
        "crazyDeals": [p for p in products if p["price"] <= 0.19],
        "bigDiscounts": [p for p in products if p["discount"] >= 40 and p["price"] > 0.19]
    }
}

with open("kaufland.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

