from datetime import datetime
from core.events import MarketEvent

class DataNormalizer:
    @staticmethod
    def normalize(raw_data: dict, source: str) -> MarketEvent:
        '''
        Converts raw broker data into our standard MarketEvent format.
        '''
        return MarketEvent(
            symbol=raw_data.get('symbol', 'UNKNOWN').upper(),
            asset_class=raw_data.get('asset_class', 'UNKNOWN').upper(),
            bid=float(raw_data.get('bid', 0.0)),
            ask=float(raw_data.get('ask', 0.0)),
            last=float(raw_data.get('last', 0.0)),
            volume=float(raw_data.get('volume', 0.0)),
            timestamp=datetime.utcnow(),
            source=source
        )
