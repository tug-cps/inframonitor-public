import datetime as dt
from abc import abstractmethod

from mqttagent.pipeline import Topic


class Operation:
    @abstractmethod
    def process(self, timestamp: dt.datetime, topic: Topic, payload: any) -> bool:
        """Process payload"""
