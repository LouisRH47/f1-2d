from .silverstone import create_track as silverstone
from .monaco import create_track as monaco
from .monza import create_track as monza

TRACKS = {
    "Silverstone": silverstone,
    "Monaco": monaco,
    "Monza": monza,
}
