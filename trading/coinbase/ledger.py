"""
Trade ledger — append-only JSONL logging with P&L tracking.
"""
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class TradeRecord:
    timestamp: float
    pair: str
    side: str
    price: float
    quantity: float
    quote_amount: float
    fee: float
    order_id: str
    strategy: str
    signal: str
    dry_run: bool
    pnl: Optional[float] = None
    notes: str = ""


class Ledger:
    def __init__(self, path: str = "trades.jsonl"):
        self.path = path
        d = os.path.dirname(self.path)
        if d:
            os.makedirs(d, exist_ok=True)

    def log(self, record: TradeRecord):
        with open(self.path, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def read_all(self) -> list:
        if not os.path.exists(self.path):
            return []
        records = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def today_pnl(self) -> float:
        today_start = time.time() - (time.time() % 86400)
        total = 0.0
        for r in self.read_all():
            if r.get("timestamp", 0) >= today_start and r.get("pnl") is not None:
                total += r["pnl"]
        return total

    def recent_results(self, n: int = 10) -> list:
        all_trades = [r for r in self.read_all() if r.get("pnl") is not None]
        return all_trades[-n:]

    def summary(self) -> dict:
        records = self.read_all()
        closed = [r for r in records if r.get("pnl") is not None]
        if not closed:
            return {"total_trades": len(records), "closed": 0, "total_pnl": 0.0}
        wins = [r for r in closed if r["pnl"] > 0]
        losses = [r for r in closed if r["pnl"] <= 0]
        total_pnl = sum(r["pnl"] for r in closed)
        return {
            "total_trades": len(records),
            "closed": len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(closed) if closed else 0,
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(total_pnl / len(closed), 2),
            "best_trade": round(max(r["pnl"] for r in closed), 2),
            "worst_trade": round(min(r["pnl"] for r in closed), 2),
        }
