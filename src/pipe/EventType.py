from enum import Enum


class EventType(Enum):
    """
    Enumeration to make EventTypes on hltv.org more human readable
    """
    ALL = 'ALL'
    MAJOR = 'MAJOR'
    INTERNATIONAL_LAN = 'INTLLAN'
    REGIONAL_LAN = 'REGIONALLAN'
    ONLINE = 'ONLINE'
    LOCAL_LAN = 'LOCALLAN'

    def __str__(self):
        return self.name
