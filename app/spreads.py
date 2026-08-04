from itertools import combinations


def calculate_spreads(prices: list[dict]) -> list[dict]:
    spreads = []
    for a, b in combinations(prices, 2):
        buy_b_sell_a = a["bid"] - b["ask"]
        buy_a_sell_b = b["bid"] - a["ask"]
        spreads.append({
            "direction": f"buy_{b['exchange']}_sell_{a['exchange']}",
            "raw": round(buy_b_sell_a, 2),
            "raw_pct": round(buy_b_sell_a / b["ask"] * 100, 4),
        })
        spreads.append({
            "direction": f"buy_{a['exchange']}_sell_{b['exchange']}",
            "raw": round(buy_a_sell_b, 2),
            "raw_pct": round(buy_a_sell_b / a["ask"] * 100, 4),
        })
    return spreads
