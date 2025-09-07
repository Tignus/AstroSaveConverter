"""Enumeration describing the supported conversion directions."""

from enum import Enum, auto


class AstroConvType(Enum):
    """Possible conversion types for AstroSaveConverter."""

    WIN2STEAM = auto()
    STEAM2WIN = auto()
