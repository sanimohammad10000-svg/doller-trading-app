import csv
from datetime import datetime
from core.events import MarketEvent

class HistoricalDataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        events = []
        with open(self.file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                event = MarketEvent(
                    symbol=row['symbol'],
                    asset_class=row['asset_class'],
                    bid=float(row['bid']),
                    ask=float(row['ask']),
                    last=float(row['last']),
                    volume=float(row['volume']),
                    timestamp=datetime.utcnow(),
                    source="historical_csv"
                )
                events.append(event)
        return events
