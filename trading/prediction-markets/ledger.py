"""
Trade ledger — append-only JSONL log.
"""

import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class TradeRecord:
    timestamp: float
    platform: str
    market_id: str
    market_title: str
    side: str
    price: float
    size: float
    leader_id: str
    signal_source: str
    pnl: float = 0.0
    fees: float = 0.0
    dry_run: bool = False
    order_id: str = ""
    notes: str = ""


class Ledger:
    def __init__(self, filepath: str = "data/trades.jsonl"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    def log(self, record: TradeRecord):
        with open(self.filepath, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def read_all(self) -> list[TradeRecord]:
        records = []
        if not os.path.exists(self.filepath):
            return records
        with open(self.filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(TradeRecord(**json.loads(line)))
        return records

    def recent(self, n: int = 20) -> list[TradeRecord]:
        """Return last N trades."""
        all_records = self.read_all()
        return all_records[-n:]

    def summary(self) -> dict:
        records = self.read_all()
        total_pnl = sum(r.pnl for r in records)
        total_fees = sum(r.fees for r in records)
        return {
            "total_trades": len(records),
            "total_pnl": round(total_pnl, 4),
            "total_fees": round(total_fees, 4),
            "net": round(total_pnl - total_fees, 4),
        }
