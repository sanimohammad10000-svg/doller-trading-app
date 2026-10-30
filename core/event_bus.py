import logging
from collections import defaultdict
from typing import Callable, Type
from core.events import Event

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]):
        self._subscribers[event_type].append(handler)
        logging.info(f"Subscribed {handler.__name__} to {event_type.__name__}")

    def publish(self, event: Event):
        event_type = type(event)
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logging.error(f"Error in handler {handler.__name__} for {event_type.__name__}: {e}")
        else:
            logging.debug(f"No subscribers for event: {event_type.__name__}")
